---
type: item_filter
name: Humanoid
slots:
  head: { name: Head }
  torso: { name: Torso, unequips: [two_piece] }
  pants: { name: Pants, unequips: [two_piece] }
  main_hand: { name: Main Hand, unequips: [left_hand, right_hand] }
  left_hand: { name: Left Hand, unequips: [main_hand, right_hand] }
  right_hand: { name: Right Hand, unequips: [main_hand, left_hand] }
  two_piece: { name: Two-Piece, unequips: [torso, pants] }
  feet: { name: Feet, unequips: [feet] }
---
