from cfg.aho_ullman import *
from cfg.cfg import *
import unittest

CFG = ContextFreeGrammar

class PseudoStream(object):

    def __init__(self):
        self._strs = []

    def write(self, s):
        self._strs.append(s)

    def clear(self):
        del self._strs[:]

    def __str__(self):
        return ''.join(self._strs)

class TestAhoUllman(unittest.TestCase):

    def _test_inputs(self, func):
        with self.assertRaises(TypeError) as ar:
            func('A -> x', map(Terminal, 'x'))
        with self.assertRaises(TypeError) as ar:
            func(CFG('A -> x'), 'x')
        with self.assertRaises(ValueError) as ar:
            func(CFG('A -> x'), map(Terminal, 'y'))

    def test_topdown_backtrack_parse(self):

        self._test_inputs(topdown_backtrack_parse)
        with self.assertRaises(ValueError) as ar:
            topdown_backtrack_parse(CFG('A -> Aa | a'), map(Terminal, 'aaa'))

        # Example 4.1 from Aho & Ullman p. 292-293
        G = CFG('''
E -> T+E
E -> T
T -> F*T
T -> F
F -> a
''')
        w = map(Terminal, 'a+a')
        expected_parse = [1, 4, 5, 2, 4, 5]
        expected_tree = ParseTree(Nonterminal('E'), [
            ParseTree(Nonterminal('T'), [
                ParseTree(Nonterminal('F'), [
                    ParseTree(Terminal('a'))
                ])
            ]),
            ParseTree(Terminal('+')),
            ParseTree(Nonterminal('E'), [
                ParseTree(Nonterminal('T'), [
                    ParseTree(Nonterminal('F'), [
                        ParseTree(Terminal('a'))
                    ])
                ])
            ])
        ])
        expected_output = '''\
(q, 1, e, E$)
|- (q, 1, E1, T+E$)
|- (q, 1, E1 T1, F*T+E$)
|- (q, 1, E1 T1 F1, a*T+E$)
|- (q, 2, E1 T1 F1 a, *T+E$)
|- (b, 2, E1 T1 F1 a, *T+E$)
|- (b, 1, E1 T1 F1, a*T+E$)
|- (b, 1, E1 T1, F*T+E$)
|- (q, 1, E1 T2, F+E$)
|- (q, 1, E1 T2 F1, a+E$)
|- (q, 2, E1 T2 F1 a, +E$)
|- (q, 3, E1 T2 F1 a +, E$)
|- (q, 3, E1 T2 F1 a + E1, T+E$)
|- (q, 3, E1 T2 F1 a + E1 T1, F*T+E$)
|- (q, 3, E1 T2 F1 a + E1 T1 F1, a*T+E$)
|- (q, 4, E1 T2 F1 a + E1 T1 F1 a, *T+E$)
|- (b, 4, E1 T2 F1 a + E1 T1 F1 a, *T+E$)
|- (b, 3, E1 T2 F1 a + E1 T1 F1, a*T+E$)
|- (b, 3, E1 T2 F1 a + E1 T1, F*T+E$)
|- (q, 3, E1 T2 F1 a + E1 T2, F+E$)
|- (q, 3, E1 T2 F1 a + E1 T2 F1, a+E$)
|- (q, 4, E1 T2 F1 a + E1 T2 F1 a, +E$)
|- (b, 4, E1 T2 F1 a + E1 T2 F1 a, +E$)
|- (b, 3, E1 T2 F1 a + E1 T2 F1, a+E$)
|- (b, 3, E1 T2 F1 a + E1 T2, F+E$)
|- (b, 3, E1 T2 F1 a + E1, T+E$)
|- (q, 3, E1 T2 F1 a + E2, T$)
|- (q, 3, E1 T2 F1 a + E2 T1, F*T$)
|- (q, 3, E1 T2 F1 a + E2 T1 F1, a*T$)
|- (q, 4, E1 T2 F1 a + E2 T1 F1 a, *T$)
|- (b, 4, E1 T2 F1 a + E2 T1 F1 a, *T$)
|- (b, 3, E1 T2 F1 a + E2 T1 F1, a*T$)
|- (b, 3, E1 T2 F1 a + E2 T1, F*T$)
|- (q, 3, E1 T2 F1 a + E2 T2, F$)
|- (q, 3, E1 T2 F1 a + E2 T2 F1, a$)
|- (q, 4, E1 T2 F1 a + E2 T2 F1 a, $)
|- (t, 4, E1 T2 F1 a + E2 T2 F1 a, e)
'''
        out = PseudoStream()

        result = topdown_backtrack_parse(G, w, out)

        self.assertEqual(result, expected_parse,
            'Production number list is correct')
        self.assertEqual(LeftParse(G, result).tree(), expected_tree,
            'Parse tree is correct')
        self.assertEqual(str(out), expected_output,
            'State transition output is correct')

        for ww in 'a a*a a+a*a a*a+a a+a+a'.split():
            self.assertIsNot(topdown_backtrack_parse(G, map(Terminal, ww)), None,
                'Succeeds on input %r' % ww)
        for ww in [''] + '+ * aa a+a+ a+a*'.split():
            with self.assertRaises(ParseError) as ar:
                topdown_backtrack_parse(G, map(Terminal, ww))

    def test_bottomup_backtrack_parse(self):

        self._test_inputs(bottomup_backtrack_parse)
        with self.assertRaises(ValueError) as ar:
            bottomup_backtrack_parse(CFG('A -> '), map(Terminal, ''))
        with self.assertRaises(ValueError) as ar:
            bottomup_backtrack_parse(CFG('A -> B | a\nB -> A'), map(Terminal, 'a'))

        # Example 4.4 from Aho & Ullman p. 304-305
        G = CFG('''
E -> E+T
E -> T
T -> T*F
T -> F
F -> a
''')
        w = map(Terminal, 'a*a')
        expected_parse = [2, 3, 5, 4, 5]
        expected_tree = ParseTree(Nonterminal('E'), [
            ParseTree(Nonterminal('T'), [
                ParseTree(Nonterminal('T'), [
                    ParseTree(Nonterminal('F'), [
                        ParseTree(Terminal('a'))
                    ])
                ]),
                ParseTree(Terminal('*')),
                ParseTree(Nonterminal('F'), [
                    ParseTree(Terminal('a'))
                ])
            ])
        ])
        expected_output = '''\
(q, 1, $, e)
|- (q, 2, $a, s)
|- (q, 2, $F, 5s)
|- (q, 2, $T, 45s)
|- (q, 2, $E, 245s)
|- (q, 3, $E*, s245s)
|- (q, 4, $E*a, ss245s)
|- (q, 4, $E*F, 5ss245s)
|- (q, 4, $E*T, 45ss245s)
|- (q, 4, $E*E, 245ss245s)
|- (b, 4, $E*E, 245ss245s)
|- (b, 4, $E*T, 45ss245s)
|- (b, 4, $E*F, 5ss245s)
|- (b, 4, $E*a, ss245s)
|- (b, 3, $E*, s245s)
|- (b, 2, $E, 245s)
|- (q, 3, $T*, s45s)
|- (q, 4, $T*a, ss45s)
|- (q, 4, $T*F, 5ss45s)
|- (q, 4, $T, 35ss45s)
|- (q, 4, $E, 235ss45s)
|- (t, 4, $E, 235ss45s)
'''
        out = PseudoStream()

        result = bottomup_backtrack_parse(G, w, out)

        self.assertEqual(result, expected_parse,
            'Production number list is a right parse in reverse')
        result_tree = RightParse(G, list(reversed(result))).tree()
        self.assertEqual(result_tree, expected_tree,
            'Parse tree is correct')
        self.assertEqual(str(out), expected_output,
            'State transition output is correct')

        for ww in 'a a*a a+a*a a*a+a a+a+a'.split():
            self.assertIsNot(bottomup_backtrack_parse(G, map(Terminal, ww)), None,
                'Succeeds on input %r' % ww)
        for ww in [''] + '+ * aa a+a+ a+a*'.split():
            with self.assertRaises(ParseError) as ar:
                bottomup_backtrack_parse(G, map(Terminal, ww))

if __name__ == '__main__':
    unittest.main()


