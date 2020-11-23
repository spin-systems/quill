def create_ns_alias_file(par):
    file_path = par / "alias.mmd"
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
    with open(file_path, "w") as f:
        f.write("\n".join(lines))


def create_routing_table(par):
    file_path = par / "routing.mmd"
    lines = [
        "-spin.systems=",
        "",
        "-spin:",
        "-:log=",
        "-,:ocu=",
        "-,:arc=",
        "-,:erg=",
        "-,:opt=",
        "-,:arb=",
        "-,:doc=",
        "",
        "-qu:",
        "-:cal=",
        "-,:conf=",
        "-,:pore=",
        "-,:qrx=",
        "-,:poll=",
        "-,:reed=",
        "-,:noto=",
        "-,:plot=",
        "-,:labs=",
    ]
    with open(file_path, "w") as f:
        f.write("\n".join(lines))
