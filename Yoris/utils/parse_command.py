def split_enable_trigger_args(text: str) -> list[str]:
    """
    Разбивает строку на аргументы по пробелу, но объединяет все, что в `...` в один блок.
    """
    args = []
    buffer = ""
    in_tick = False
    i = 0
    while i < len(text):
        c = text[i]
        if c == '"':
            in_tick = not in_tick
            i += 1
            continue
        if c == ' ' and not in_tick:
            if buffer:
                args.append(buffer)
                buffer = ""
            i += 1
            continue
        buffer += c
        i += 1
    if buffer:
        args.append(buffer)
    return args
