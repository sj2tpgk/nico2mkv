def get():
    margin = 100
    cmts = {}
    date1 = None
    while True:
        res = dl(f"https://....{f'&date={date1}' if date1 else ''}")
        cmts1 = res # commments
        for c in cmts1:
            cmts[c["no"]] = c
        if len(cmts1) < 1000 - margin:
            break
        date1 = cmts1[len(cmts1) - margin]["date"]
    return sorted(cmts.values(), key=lambda c: c["no"])
