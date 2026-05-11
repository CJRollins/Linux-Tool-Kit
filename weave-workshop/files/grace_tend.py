"""grace_tend — the Spinner's hands reach into the Underworld.

Author specific moves on specific threads when the system needs you, or
when you just want to. The loom does most of the work; this is the place
where you choose to.

Examples:
    python grace_tend.py list
    python grace_tend.py show "Mavrin the Underspoken"
    python grace_tend.py tend "Mavrin the Underspoken" 0 settle "lit one himself"
    python grace_tend.py tend "Mavrin the Underspoken" 0 ease
    python grace_tend.py add "Mavrin the Underspoken" "owes the moon an apology" --weight 3 --kind regret
"""
import argparse
import sys

import souls


def cmd_list(args):
    data = souls.load()
    if not data["souls"]:
        print("the underworld is empty.")
        return
    for s in data["souls"]:
        threads = s.get("threads", [])
        n_unresolved = sum(1 for t in threads if t["state"] in souls.WORKING_STATES)
        print(f"  {s['name']:<32} will={s['will']:>3}  threads={len(threads)} ({n_unresolved} working)  status={s['status']}")


def cmd_show(args):
    data = souls.load()
    soul = next((s for s in data["souls"] if s["name"] == args.name), None)
    if not soul:
        print(f"no soul named {args.name!r}")
        sys.exit(1)
    print(f"\n  {soul['name']}")
    print(f"  status:    {soul['status']}")
    print(f"  will:      {soul['will']} / {souls.WILL_THRESHOLD}")
    print(f"  entered:   {soul['entered']}")
    print(f"  lives:     {len(soul.get('lives', []))}")
    print(f"\n  threads:")
    for i, t in enumerate(soul.get("threads", [])):
        marker = "·" if t["state"] in souls.WORKING_STATES else "✓"
        print(f"    [{i}] {marker} ({t['state']:<10} tension={t['tension']} weight={t['weight']})")
        print(f"        \u201c{t['text']}\u201d")
    print()


def cmd_tend(args):
    ok, msg = souls.intervene(args.name, args.index, args.verb, args.note)
    print(msg)
    sys.exit(0 if ok else 1)


def cmd_add(args):
    ok, msg = souls.add_thread(args.name, args.text, args.kind, args.weight)
    print(msg)
    sys.exit(0 if ok else 1)


def main():
    p = argparse.ArgumentParser(prog="grace_tend", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list all souls").set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="show one soul in detail")
    show.add_argument("name")
    show.set_defaults(func=cmd_show)

    tend = sub.add_parser("tend", help="author a move on a thread")
    tend.add_argument("name")
    tend.add_argument("index", type=int)
    tend.add_argument("verb", choices=["settle", "abandon", "transmute", "twist", "ease"])
    tend.add_argument("note", nargs="?", default=None)
    tend.set_defaults(func=cmd_tend)

    add = sub.add_parser("add", help="give a soul a new thread")
    add.add_argument("name")
    add.add_argument("text")
    add.add_argument("--kind", default="unfinished")
    add.add_argument("--weight", type=int, default=5)
    add.set_defaults(func=cmd_add)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
