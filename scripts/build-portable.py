"""
Rebuild the "complete" opencode desktop exe with the TokenRhythm provider preset baked in.

The official opencode desktop Windows installer (opencode-desktop-win-x64.exe) is an
electron-builder NSIS one-click installer that stores the app as a raw 7z archive. This
script:

  1. locates and extracts that 7z from the official exe (with 7-Zip),
  2. patches the bundled opencode server so the first-run default config is the
     TokenRhythm provider preset (written to ~/.config/opencode/opencode.jsonc),
  3. repacks the app folder into a fresh 7z (same codecs as the original: BCJ2 + LZMA2),
  4. reassembles the exe: original stub + padded 7z (exact original slot size) + tail.

Usage:
  python scripts/build-portable.py ^
      --exe <path-to-opencode-desktop-win-x64.exe> ^
      --config opencode.jsonc ^
      --out opencode-desktop-win-x64-TokenRhythm.exe ^
      [--7z "C:\\Program Files\\7-Zip\\7z.exe"]
"""

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile


def find_sevenz_offset(exe_path: bytes, data: bytes) -> int:
    """Find the first '7z' archive signature in the exe."""
    sig = b"\x37\x7a\xbc\xaf\x27\x1c"
    idx = data.find(sig)
    if idx < 0:
        raise RuntimeError("no embedded 7z archive found in " + exe_path)
    return idx


def read_asar_header(path):
    with open(path, "rb") as f:
        f.read(4)  # pickle size
        header_block_size = struct.unpack("<I", f.read(4))[0]
        f.read(4)  # pickle payload size
        header_string_size = struct.unpack("<I", f.read(4))[0]
        header = f.read(header_string_size)
        base = 8 + header_block_size
        return json.loads(header.decode("utf-8")), base


def asar_walk(container, prefix=""):
    for name, child in container.items():
        full = prefix + "/" + name
        if "files" in child:
            yield from asar_walk(child["files"], full)
        else:
            yield full, child


def asar_extract(asar_path, out_dir):
    header, base = read_asar_header(asar_path)
    with open(asar_path, "rb") as f:
        for full, entry in asar_walk(header["files"]):
            target = os.path.join(out_dir, full.lstrip("/"))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if "offset" in entry:
                f.seek(base + int(entry["offset"]))
                data = f.read(entry["size"])
                with open(target, "wb") as w:
                    w.write(data)
            else:
                open(target, "wb").close()
    return header


def asar_pack(header, app_dir, out_path):
    files = []
    for full, entry in asar_walk(header["files"]):
        files.append((full, entry))

    segments = []
    for full, entry in files:
        if entry.get("unpacked"):
            segments.append((full, entry, None))
            continue
        rel = full.lstrip("/")
        segments.append((full, entry, os.path.join(app_dir, rel.replace("/", os.sep))))

    offset = 0
    for full, entry, disk in segments:
        if disk is None:
            entry.pop("offset", None)
            continue
        size = os.path.getsize(disk)
        entry["size"] = size
        entry["offset"] = str(offset)
        offset += size

    header_bytes = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    strlen = len(header_bytes)
    padding = (4 - (16 + strlen) % 4) % 4
    inner_payload = 4 + strlen + padding
    header_block_size = 8 + strlen + padding

    with open(out_path, "wb") as out:
        out.write(struct.pack("<I", 4))
        out.write(struct.pack("<I", header_block_size))
        out.write(struct.pack("<I", inner_payload))
        out.write(struct.pack("<I", strlen))
        out.write(header_bytes)
        out.write(b"\x00" * padding)
        for full, entry, disk in segments:
            if disk is None:
                continue
            with open(disk, "rb") as f:
                out.write(f.read())


def patch_server_chunk(asar_extract_dir, config):
    """Replace the first-run default config inside the bundled opencode server chunk."""
    target = b'JSON.stringify({ $schema: "https://opencode.ai/config.json" }, null, 2)'
    new_expr = b"JSON.stringify(" + json.dumps(config, ensure_ascii=False).encode("utf-8") + b", null, 2)"

    chunks_dir = os.path.join(asar_extract_dir, "out", "main", "chunks")
    if not os.path.isdir(chunks_dir):
        raise RuntimeError("out/main/chunks not found in asar; opencode layout changed?")

    patched = False
    for name in sorted(os.listdir(chunks_dir)):
        path = os.path.join(chunks_dir, name)
        if not os.path.isfile(path) or not name.startswith("node-"):
            continue
        with open(path, "rb") as f:
            data = f.read()
        if target in data:
            if data.count(target) != 1:
                raise RuntimeError("default config marker found %d times in %s" % (data.count(target), name))
            with open(path, "wb") as f:
                f.write(data.replace(target, new_expr))
            print("patched server chunk:", name)
            patched = True
            break
    if not patched:
        raise RuntimeError("default config marker not found in any server chunk")


def run7z(sevenz, args):
    subprocess.run([sevenz] + args, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True, help="official opencode-desktop-win-x64.exe")
    ap.add_argument("--config", required=True, help="opencode.jsonc provider preset")
    ap.add_argument("--out", required=True, help="output exe path")
    ap.add_argument("--7z", dest="sevenz", default=None, help="path to 7z.exe (auto-detect if omitted)")
    ap.add_argument("--workdir", default=None, help="temp work dir (default: system temp)")
    args = ap.parse_args()

    sevenz = args.sevenz
    if sevenz is None:
        for cand in [r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"]:
            if os.path.exists(cand):
                sevenz = cand
                break
    if sevenz is None:
        if shutil.which("7z"):
            sevenz = shutil.which("7z")
    if sevenz is None:
        raise RuntimeError("7-Zip not found; pass --7z <path>")

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    workdir = args.workdir or tempfile.mkdtemp(prefix="opencode-portable-")
    exe_dir = os.path.join(workdir, "exe")
    app_dir = os.path.join(workdir, "app")
    asar_dir = os.path.join(workdir, "asar")
    os.makedirs(exe_dir, exist_ok=True)
    os.makedirs(app_dir, exist_ok=True)

    print("[1/5] locating embedded 7z in", args.exe)
    with open(args.exe, "rb") as f:
        exe_bytes = f.read()
    sevenz_offset = find_sevenz_offset(args.exe, exe_bytes)
    print("      embedded 7z at offset", sevenz_offset)

    print("[2/5] extracting embedded 7z")
    payload = os.path.join(workdir, "payload.7z")
    with open(payload, "wb") as f:
        f.write(exe_bytes[sevenz_offset:])
    run7z(sevenz, ["x", payload, "-o" + app_dir, "-y"])

    asar_src = os.path.join(app_dir, "resources", "app.asar")
    print("[3/5] patching app.asar with TokenRhythm preset")
    header = asar_extract(asar_src, asar_dir)
    patch_server_chunk(asar_dir, config)
    asar_packed = os.path.join(workdir, "app-patched.asar")
    asar_pack(header, asar_dir, asar_packed)
    shutil.copyfile(asar_packed, asar_src)

    print("[4/5] repacking app folder (BCJ2 + LZMA2:22, non-solid)")
    new7z = os.path.join(workdir, "patched.7z")
    run7z(sevenz, ["a", "-t7z", "-mx=9", "-ms=off", "-mtc=off", "-mta=off", "-md=4m", new7z, os.path.join(app_dir, "*")])

    # determine the original 7z's declared physical size so we can pad to the exact slot
    orig_payload_len = _sevenz_physical_size(payload)
    new_size = os.path.getsize(new7z)
    if new_size > orig_payload_len:
        raise RuntimeError("new 7z (%d) exceeds the installer slot (%d); lower -md or raise -mx" % (new_size, orig_payload_len))

    print("[5/5] reassembling exe")
    tail_start = sevenz_offset + orig_payload_len
    stub = exe_bytes[:sevenz_offset]
    tail = exe_bytes[tail_start:]
    with open(args.out, "wb") as f:
        f.write(stub)
        with open(new7z, "rb") as nf:
            f.write(nf.read())
        f.write(b"\x00" * (orig_payload_len - new_size))
        f.write(tail)

    print("done:", args.out, os.path.getsize(args.out), "bytes")


def _sevenz_physical_size(sevenz_path):
    """Compute the archive's physical size from its start header.

    Layout: 6-byte signature + 2-byte version + 4-byte StartHeaderCRC
    + 8-byte NextHeaderOffset + 8-byte NextHeaderSize + 4-byte NextHeaderCRC.
    The archive ends at 32 + NextHeaderOffset + NextHeaderSize.
    """
    with open(sevenz_path, "rb") as f:
        head = f.read(32)
    if head[:6] != b"\x37\x7a\xbc\xaf\x27\x1c":
        raise RuntimeError("not a 7z archive")
    next_header_offset = struct.unpack("<q", head[12:20])[0]
    next_header_size = struct.unpack("<q", head[20:28])[0]
    return 32 + next_header_offset + next_header_size


if __name__ == "__main__":
    main()
