import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from tbgrep import TracebackGrep

traceback = 'Traceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nException\n'

variations = [
"""
foo
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
Exception
bar
""",
"""
    foo
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    Exception
    bar
""",
"""
prefix    foo
prefix    Traceback (most recent call last):
prefix      File "<stdin>", line 1, in <module>
prefix    Exception
prefix    bar
""",
]

def test_tbgrep():
    extractor = TracebackGrep()
    for variation in variations:
        found = False
        for line in variation.split('\n'):
            tb = extractor.process(line + '\n')
            if tb:
                found = True
                assert tb == traceback, repr(tb)
        assert found, "Couldn't extract traceback from: " + repr(variation)

def test_tbgrep_stats():
    extractor = TracebackGrep(stats=True)
    for variation in variations:
        for line in variation.split('\n'):
            extractor.process(line + '\n')
    stats = extractor.get_stats()
    assert len(stats) == 1, stats
    assert stats[0][1] == 3, stats[0][1]
    sys.stdout = StringIO()
    extractor.print_stats()
    assert '1 unique traceback extracted' in sys.stdout.getvalue()
    sys.stdout = sys.__stdout__

def test_command():
    from tbgrep.commands import main
    import sys
    orig_stdin = sys.stdin
    for variation in variations:
        stdin = StringIO()
#        stdin.write(variation)
        sys.stdin = stdin
        sys.argv = ['tbgrep', '--stats']
        main()
        assert '1 unique traceback extracted' in sys.stdout.getvalue(), sys.stdout
    sys.stdin = orig_stdin
