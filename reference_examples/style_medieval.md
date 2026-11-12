# Style: medieval kingdoms (second reference)

Source: 5 frames the user shared (kings at a war table, king in a field with an army,
aerial river with two armies and a bridge, "YEARS AT WAR 100" sign, sweating blacksmith).
Code: `animator/style3.py` (characters), `animator/medieval.py` (sets and props).
Use this style when the user asks for the "kings / medieval / war" look.

## Characters (`style3.Char3`), pixel-measured on the reference
- **2D drawings with soft painted light, not 3D models:** gradient lit from the upper-left and shaded toward the lower-right, no gloss. A thin light "sticker" rim runs around every character outside the dark outline.
- **Head:** wide, slightly flat cream-white oval (`#fcf6ef`), width about 1.25x its height, soft shade at the lower-right.
- **Height varies by character:** kings are tall, with total height (crown to feet) = 3.65x the head width, long legs (`legs=2.75, torso=2.05`). The blacksmith and the old man are shorter (`legs=2.0, torso=2.0` or defaults).
- **Body:** bean shape, about 0.7x the head width, small belly. Robes and capes: the cape flows to one side behind, and the legs stay visible.
- **Limbs:** THICK dark-brown limbs (about 5.5% of the head width), big dark ball hands, rounded dark feet.
- **Face:** small black oval eyes, thick brows, short mouth. Red king: small brown pointed goatee and a toothy grin. Teal king: wide white beard with strands and smug half-lidded eyes. Blacksmith: big brown handlebar moustache, tired half-lidded eyes, big orange apron, money bags with "$".
- **Crowns:** gold with sharp spikes, white balls on the tips and red/blue gems. Silver with rounded bumps and teal gems.

## How a frame is made
3D background plate rendered in Blender (`render3d/terrace_v2.py` with `NOCHARS=1`): sunlit terrace, parapet, banners, painted backdrop pre-blurred for depth of field. The 2D characters (`style3`) and their long diagonal floor shadows (`medieval.cast_shadow`) are composited on top by the animator. This matches the reference: 2D characters in a 3D world.

## Sets (`medieval.py`)
- **Painted backdrop, out of focus:** blue sky gradient (`#5f88d0` → `#a9cdf3`), puffy white clouds with lavender undersides, blue mountains with snow caps, castles with red and teal roofs, green hills and trees. Always drawn through `blurred()` with a light haze, so characters pop.
- **Sunlit stone terrace:** warm tiles (`#d6bd9f`) in perspective, long diagonal shadows from every character and prop (`cast_shadow`), stone parapet with scratched tally marks (time passing).
- **Props:** red/teal banners on poles, anvil on a tree stump (sparks), barrel full of spears, round red/teal war table as a foreground frame, "YEARS AT WAR" flip-number sign, rusty helmets with flowers growing out of them.
- **Battlefield:** farmland with crop rows and a dirt track running to the vanishing point, rows of soldiers receding.
- **Aerial:** river running away from camera (narrower far away), patchwork fields, two dense armies with flags on each bank, stone bridge across the lower third, a tiny duck family in the river.

## Camera angles (one per reference frame)
1. **Eye-level group shot on the terrace:** characters fill the frame from the waist up to the crowns, a foreground object at the bottom edge (war table, anvil) for depth, blurred landscape behind.
2. **Low ground angle:** camera almost at grass level, big blurred grass and flowers in front, a character mid-frame, an army line receding into the distance.
3. **High aerial (drone):** looking down the river; the tiny characters on the bridge are the story, the armies give scale. Good for reveals ("finally", "for 100 years").
4. **Prop close-up with story detail:** the sign fills the frame, a character beside it, foreground details that tell time passed (flowers growing in old helmets).
5. **Action medium:** one character reacting (sweat, shaking), others framing him on both sides, motion lines.

Everything in `visual_grammar.md` still applies: a new framing every 2-4 words landing on the key word, crane/drone moves between framings, subject between y 250 and 820, default no lip-sync, no captions, no whoosh, SFX at 10%.
