#!/usr/bin/env python3
"""Make a music bed of a given length from a loopable track: trims edge
silence, then chains copies with 2 s crossfades until the target length,
and trims to it. Usage: python3 scripts/bgm-extend.py in.mp3 out.wav SECONDS"""
import subprocess, sys, math, os, tempfile

src, out, target = sys.argv[1], sys.argv[2], float(sys.argv[3])
XF = 2.0
def dur(f):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',f]).decode().strip())

with tempfile.TemporaryDirectory(prefix='bgm-') as td:
    trim = os.path.join(td, 'trim.wav')
    # 1. trim leading/trailing silence
    subprocess.run(['ffmpeg','-y','-v','error','-i',src,'-af',
        'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse',
        trim], check=True)
    d = dur(trim)
    n = max(1, math.ceil((target + XF) / (d - XF)))
    inputs = []
    for _ in range(n): inputs += ['-i', trim]
    if n == 1:
        fc = f'[0:a]atrim=0:{target},asetpts=N/SR/TB[a]'
    else:
        chain = '[0:a][1:a]acrossfade=d=%s:c1=tri:c2=tri[x1]' % XF
        for i in range(2, n): chain += f';[x{i-1}][{i}:a]acrossfade=d={XF}:c1=tri:c2=tri[x{i}]'
        fc = chain + f';[x{n-1}]atrim=0:{target},asetpts=N/SR/TB[a]'
    subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',fc,'-map','[a]',out], check=True)
    print(f'source {d:.1f}s x{n} with {XF}s crossfades -> {dur(out):.2f}s : {out}')
