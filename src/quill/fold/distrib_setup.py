def create_ns_alias_file(par):
    alias_file_path = par / "alias.mmd"
    lines = [
        "-spin.systems=ss",
        "",
        "-spin=∫:",
        "-:log=",
        "-,:ocu=",
        "-,:arc=app",
        "-,:erg=",
        "-,:opt=",
        "-,:arb=",
        "-,:doc=",
        "",
        "-qu=q:",
        "-:cal=",
        "-,:conf=",
        "-,:pore=biorx",
        "-,:qrx=arx",
        "-,:poll=",
        "-,:reed=",
        "-,:noto=ruinoto",
        "-,:plot=plotspot",
        "-,:labs=",
    ]
    with open(alias_file_path, "w") as f:
        f.write("\n".join(lines))
