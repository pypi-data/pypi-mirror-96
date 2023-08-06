'''
This code for this progress bar is based on
vladignatyev/progress.py
https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
(MIT License)
'''
import shutil
import sys


class ProgressBar:
    def __init__(self, total, status):
        self._bar_len = 60
        self._cancelled = False
        self.reset(total=total, status=status)

    def reset(self, symbol_done="=", symbol_space=" ", total=100, status=''):
        self.con_width = shutil.get_terminal_size(fallback=(80,24)).columns
        self._symbol_done = symbol_done
        self._symbol_space = symbol_space
        self._total = total
        self._status = status
        self._count = 0

    def _disp(self, _, fetched):
        self._progress(fetched, self._total)

    def _progress(self, fillin, total):
        if total == 0 or self._cancelled:
            return
        self._count += fillin
        filled_len = int(round(self._bar_len * self._count / float(total)))
        percents = round(100.0 * self._count / float(total), 1)
        if percents > 100:
            percents = 100.0
        if filled_len > self._bar_len:
            filled_len = self._bar_len
            
        bar = self._symbol_done * filled_len + \
            self._symbol_space * (self._bar_len - filled_len)
        disp = f" [{bar}] {percents:>5.1f}% ...{self._status} "[:self.con_width - 1] + '\r'

        sys.stdout.write(disp)
        sys.stdout.flush()

    def close(self):
        if not self._cancelled:
            self._progress(self._total, self._total)

    def cancel(self):
        self._cancelled = True
    
    def is_cancelled(self):
        return self._cancelled
