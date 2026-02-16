import unittest
import os
import sys

# Ensure project root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from game.python import compile_data

class TestParseQuestTicks(unittest.TestCase):
    def test_simple_trigger_parse(self):
        body = """
## Collect Rations
```trigger
event: ITEM_GAINED
item: ration_bar
total: 5
```
"""
        ticks = compile_data.parse_quest_ticks(body, 'ration_run', source_path='data/quests/ration_run.md')
        self.assertIsInstance(ticks, list)
        self.assertEqual(len(ticks), 1)
        t = ticks[0]
        self.assertEqual(t['id'], 'collect_rations')
        self.assertIn('trigger', t)
        trig = t['trigger']
        self.assertEqual(trig.get('event'), 'ITEM_GAINED')
        self.assertEqual(str(trig.get('total')), '5')

    def test_cond_directive_uses_resolver(self):
        def resolver(expr, source_path=None, line_no=None):
            self.assertEqual(expr, "flag_get('x')")
            self.assertEqual(source_path, "data/test.md")
            self.assertEqual(line_no, 42)
            return "_cond_expr_deadbeef"

        line = "@cond \"flag_get('x')\" SOME_LABEL OTHER_LABEL"
        out = compile_data.directive_to_python(
            line,
            cond_resolver=resolver,
            source_path="data/test.md",
            line_no=42,
        )
        self.assertEqual(out, "cond_jump(_cond_expr_deadbeef, 'SOME_LABEL', 'OTHER_LABEL')")

if __name__ == '__main__':
    unittest.main()
