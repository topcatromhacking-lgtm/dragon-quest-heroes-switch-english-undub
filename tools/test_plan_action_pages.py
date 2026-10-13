#!/usr/bin/env python3
"""Synthetic pagination regression tests; includes no game text."""
import unittest
from plan_action_list_pages import paginate, normalize, visible_units


class PaginationTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(paginate(''), [''])

    def test_simple(self):
        self.assertEqual(paginate('Small test.'), ['Small test.'])

    def test_two_pages_preserve_every_word(self):
        s = ' '.join(['once','upon','a','time','the','uninterrupted','message',
                      'needs','more','space'] * 4)
        pages = paginate(s)
        self.assertGreater(len(pages), 1)
        self.assertEqual(normalize(' '.join(pages)), normalize(s))
        self.assertTrue(all(visible_units(p) <= 58 for p in pages))
        self.assertTrue(all(visible_units(l) <= 39 for p in pages for l in p.split('\n')))

    def test_controller_tokens(self):
        s = 'Press \x1bP2 to start, then hold \x1bP3 to execute another action.'
        pages = paginate(s)
        self.assertEqual(normalize(' '.join(pages)), s)
        self.assertEqual(sum(p.count('\x1bP2') for p in pages), 1)
        self.assertEqual(sum(p.count('\x1bP3') for p in pages), 1)
        self.assertEqual(visible_units('\x1bP2'), 1)

    def test_accented_word_kept(self):
        s = 'Perform a Coup de Grâce after preparing the final move.'
        self.assertEqual(normalize(' '.join(paginate(s))), s)

    def test_many_lengths(self):
        for n in range(20,40):
            s=' '.join('abcd'+'a'*(i%7+1) for i in range(n))
            pages=paginate(s)
            self.assertEqual(normalize(' '.join(pages)),s)
            self.assertTrue(all(visible_units(p)<=58 for p in pages))

    def test_reject_bad_limits(self):
        for max_units,max_cols in [(61,40),(58,60),(0,1)]:
            with self.assertRaises(ValueError):
                paginate('test',max_units,max_cols)


if __name__ == '__main__':
    unittest.main()
