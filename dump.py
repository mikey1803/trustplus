import marshal
import dis

with open('e:/fake/TrustLensPlus/__pycache__/app.cpython-313.pyc', 'rb') as f:
    f.read(16)
    code = marshal.load(f)

def dump_code(c, out):
    out.write(f"\n--- Code object: {c.co_name} ---\n")
    dis.dis(c, file=out)
    for const in c.co_consts:
        if type(const) == type(c):
            dump_code(const, out)

with open('e:/fake/TrustLensPlus/disassembled.txt', 'w', encoding='utf-8') as out:
    dump_code(code, out)
