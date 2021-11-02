__all__ = ["create_ns_aliases", "create_routing_table", "create_manifest"]

def create_ns_aliases(par):
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


def create_manifest(par):
    file_path = par / "manifest.mmd"
    lines = [
        "-spin.systems:spin-systems:master www:",
        "-:cal:qu-cal:master www",
        "-,:log:spin-log:master www",
        "-,:conf:qu-conf:master www",
        "-,:pore:qu-pore:master www",
        "-,:ocu:naiveoculus:master www",
        "-,:arc:appendens:master www",
        "-,:qrx:qu-arx:master www",
        "-,:erg:spin-erg:master www",
        "-,:opt:spin-opt:master www",
        "-,:poll:qu-poll:master www",
        "-,:arb:spin-arb:master www",
        "-,:reed:qu-reed:master www",
        "-,:noto:qu-noto:master www",
        "-,:plot:qu-plot:master www",
        "-,:doc:spin-doc:master www",
        "-,:labs:qu-labs:master www",
    ]
    with open(file_path, "w") as f:
        f.write("\n".join(lines))
