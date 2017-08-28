
def parse_time(time_str):
    chunks = time_str.split(':')
    time = 0.0
    mult = [1., 60., 3600., 3600.*24]
    if len(chunks) > len(mult): raise ValueError('Not a time format I can understand')
    idx = 0
    for chunk in reversed(chunks):
        time += float(chunk) * mult[idx]
        idx  += 1
    return time

def format_time(seconds):
    hours = int(seconds // 3600)
    remainder = seconds - hours*3600
    minutes = int(remainder // 60)
    remainder = remainder - minutes*60
    seconds = remainder
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


