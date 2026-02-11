import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'game', 'python'))
import compile_helpers as ch


def test_extract_flow_blocks():
    lines = [
        (10, "Some intro"),
        (11, "```flow"),
        (12, "$ pc.gold = 10"),
        (13, "Renpy: text"),
        (14, "```"),
    ]
    blocks = ch.extract_flow_blocks(lines)
    assert isinstance(blocks, list)
    assert len(blocks) == 1
    blk = blocks[0]
    assert blk['start_line'] == 12
    assert blk['lines'][0][1].strip().startswith('$')


def test_extract_yaml_block():
    lines = [
        (20, "Intro"),
        (21, "```yaml"),
        (22, "menu: clerk"),
        (23, "id: ask_clerk"),
        (24, "```"),
        (25, "After")
    ]
    data, cleaned = ch.extract_yaml_block(lines)
    assert isinstance(data, dict)
    assert data.get('menu') == 'clerk'
    assert isinstance(cleaned, list)
