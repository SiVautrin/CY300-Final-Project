## CDT Silas Smith, CDT Daniel Walsh

## LTC John Hutton

## CY300

## 09 OCT 2026

## **Development Plan: Rock, Paper, Magic**

## **1\. Introduction / Overview**

Rock, Paper, Magic is a local, two-player, turn-based strategy game built in Python with Pygame. Players battle by drawing spells: each round, both players secretly draw a single-stroke glyph on a parchment canvas, and the game recognizes which of nine spells was cast and how accurately it was drawn.

Each spell combines one of three elements (Fire, Earth, Wind) with one of three types (Attack, Heal, Block). Both spells resolve simultaneously, so success depends on drawing skill and on anticipating the opponent's choice.

Drawing-based spellcasting appears in a few commercial games. Treating drawing accuracy as a skill axis inside a simultaneous-turn PvP counter system is an uncommon design space, and that combination is the focus of this project.

### **Goals**

1. **Playable PvP loop:** Two players can complete a full match on one device, from start to a declared winner or draw, with no developer intervention.  
2. **Skill-based casting:** The game identifies which of 9 spells was drawn using the \$1 Unistroke Recognizer. Drawing accuracy scales spell power, and drawings below 50% accuracy fizzle.  
3. **Strategic depth:** Elemental and type interactions mean the best spell depends on the opponent's simultaneous choice.  
4. **Readable feedback:** Players can see what each side cast and how the exchange resolved, through spell visuals and HP changes.

## **2\. Overview of Features**

The game supports seven player-facing (explicit) features and four under-the-hood (implicit) features.

### **Explicit features**

1. Display an arena with Player 1 on top and Player 2 on the bottom, each with a visible HP bar.  
2. Show a 5-second "Get ready" countdown at the start of each round.  
3. Present a parchment canvas where the active player draws a single mouse stroke and submits it with a Cast button.  
4. Show a handoff screen ("Pass to Player 2, press SPACE when ready") that hides Player 1's drawing to keep spell choices secret.  
5. Render each cast spell (e.g., a fireball or rock wall) on the arena near its caster after resolution, and indicate fizzles.  
6. Display round results (spells cast, HP changes) before the next round begins.  
7. Show an end-of-match screen declaring the winner or a draw, with Rematch and Quit options.

### **Implicit features**

8. Load the 9 spell templates from file on startup.  
9. Recognize each stroke with the \$1 Unistroke Recognizer: classify it as the closest template and compute an accuracy score. Strokes below 50% accuracy fizzle.  
10. Resolve both spells simultaneously using effect \= base × element multiplier × accuracy, with all multipliers stored in a single editable rules table.  
11. Track match state (round number, HP, accuracy history) and check the win condition after each round.

### **Combat rules**

Elements form a triangle: Fire beats Earth, Earth beats Wind, Wind beats Fire. A spell "wins" when its element beats the opposing spell's element, "loses" when the reverse is true, and is "neutral" on a same-element matchup or when unopposed.

| Spell type | Win | Neutral | Lose |
| ----- | ----- | ----- | ----- |
| Attack (damage multiplier) | 1x | 1x | 0.5x |
| Block (damage let through) | 0x | 0.5x | 0.5x |
| Heal (HP restored) | 2 HP | 0 HP | 0 HP |

Interaction rules:

* **Attack vs. Block:** multipliers stack; the block reduces incoming damage.  
* **Attack vs. Attack:** both players take damage.  
* **Attack vs. Heal:** the heal applies and the attacker deals damage. Both are computed separately so values can be rebalanced later.  
* **Block vs. Block:** nothing happens.  
* **Heal vs. Heal:** each heal resolves by element comparison.  
* **Fizzle:** the fizzled player does nothing; the opponent's spell resolves as neutral. If both fizzle, the round ends with no effect.  
* **Heal design note:** a heal only restores HP when its element wins. This is intentional.

The match ends when a player reaches 0 HP. If both reach 0 HP in the same round, the player with the higher total drawing accuracy wins; equal accuracy is a draw.

## **3\. Code Structure**

The game uses seven classes, each with a single responsibility. Game logic (rules, recognition, player state) is kept separate from Pygame rendering, and the Game class runs a state machine that moves through COUNTDOWN, DRAWING, HANDOFF, RESULTS, and GAME\_OVER.

**Player:** holds one player's state and applies HP changes.

* *State:* name, hp, max\_hp, player\_icon, hp\_icon, accuracy\_history  
* *Behaviors:* take\_damage(amount), heal(amount), record\_accuracy(score), is\_defeated(), total\_accuracy()

**Spell:** a plain data object describing one cast spell.

* *State:* element (FIRE / WIND / EARTH), spell\_type (ATTACK / BLOCK / HEAL), accuracy, fizzled  
* *Behaviors:* is\_fizzle(), name() (e.g., returns "Fire Attack")

**CombatResolver:** owns all spell-interaction logic and the editable rules table.

* *State:* element\_chart (which element beats which), multipliers table (attack, block, and heal values for win, neutral, and lose), base values  
* *Behaviors:* compare\_elements(e1, e2), resolve(spell1, spell2) → HP changes for each player

**StrokeRecognizer:** implements the \$1 Unistroke Recognizer. Stateless apart from its templates.

* *State:* templates (9 point lists mapped to element and type), num\_resample\_points, fizzle\_threshold (0.5)  
* *Behaviors:* load\_templates(path), resample(points), normalize(points), recognize(points) → Spell

**DrawingCanvas:** captures one mouse stroke on the parchment.

* *State:* points list, is\_drawing, parchment image, cast\_button rect  
* *Behaviors:* handle\_mouse(event), clear(), get\_stroke(), draw(surface)

**Arena:** draws everything the players see. Holds no game logic.

* *State:* screen surface, background, spell\_effect images (9), fonts  
* *Behaviors:* draw\_arena(players), draw\_spell\_effects(spell1, spell2), draw\_countdown(t), draw\_handoff(next\_player), draw\_results(outcome), draw\_game\_over(winner)

**Game:** the state machine and main loop that coordinates every other class.

* *State:* current\_state, players (2), current\_turn, round\_number, pending\_spells, countdown\_timer  
* *Behaviors:* run(), handle\_event(event), change\_state(new\_state), resolve\_round(), check\_winner() (including the double-KO tiebreak and draw), reset\_match()

**Feature coverage:**

| Class | Features covered |
| ----- | ----- |
| Arena | 1, 2, 5, 6, 7 |
| DrawingCanvas | 3 |
| Game | 4, 11 |
| StrokeRecognizer | 8, 9 |
| CombatResolver | 10 |
| Player, Spell | Data used by features 9–11 |

## **4\. Minimum Viable Product**

The MVP is a complete, playable match that uses a working recognizer with 3 of the 9 planned spell templates. Stroke recognition is the project's highest-risk component, so the MVP proves it works rather than deferring it.

### **Included**

* **Full match loop:** the Game state machine cycles through countdown, Player 1 drawing, handoff, Player 2 drawing, resolution, and results, and ends when a player reaches 0 HP.  
* **Drawing and recognition:** players draw a single stroke on the DrawingCanvas. The StrokeRecognizer classifies it against 3 templates (Fire Attack, Wind Block, Earth Heal) using the \$1 Unistroke Recognizer, produces an accuracy score, and fizzles strokes below 50%.  
* **Full combat rules:** the CombatResolver applies the complete element triangle and type rules, including accuracy scaling, from the editable rules table.  
* **Basic feedback:** HP updates each round and a winner is declared.

The three MVP templates cover every element and every spell type, so every combat rule is exercised. Adding the remaining six spells only requires drawing and saving new templates.

### **Deferred**

* The remaining 6 spell templates  
* Spell visuals (the MVP shows colored shapes and text labels instead of images)  
* The Rematch and Quit end screen (the MVP ends with a winner message)  
* Double-KO tiebreak and draw handling  
* Visual polish on the parchment and arena

## **5\. Checkpoint 2**

By Checkpoint 2, all four goals and all eleven features will be implemented. Only art upgrades, polish, and test-driven fixes remain for the final stretch before peer review.

### **Complete by Checkpoint 2**

* All 9 spell templates recognized by the StrokeRecognizer  
* Basic static images for all 9 spells, appearing near each caster on resolution  
* Double-KO tiebreak (higher total accuracy wins) and draw handling  
* End-of-match screen with Rematch and Quit

### **Remaining after Checkpoint 2**

* AI-assisted art upgrades for spell visuals  
* Parchment and arena polish  
* Any spell animation  
* Fixes and tuning identified during testing

### **Testing plan**

Four players who have not seen the game will each draw every spell 3 times, for 108 total drawings. For each attempt, we will record which spell the player intended and which spell the recognizer identified.

This produces a confusion rate for each spell: how often it is misread as another spell or fizzles. Spells with high confusion rates will have their templates redrawn, and the 50% fizzle threshold will be adjusted if needed.

After playing, each tester will give feedback on whether the combat rules make sense and whether the concept is engaging. That feedback will guide any changes to the rules table.

Acknowledgement of Assistance  
Claude. Assistance given to Author, AI. Before using Claude, I wrote a significant amount of the code out myself to try and understand how I wanted my classes structured and to understand the feasibility of this project. After writing out my classes to include, a spell class, a subclass of spell for each element, a parchment class (that would handle drawing memory and accuracy), a player class, a battle class to handle gameplay, and a logic class to handle gamestages, I then started implementing these classes. I wrote out the if statement decision tree and fleshed out core mechanics and values related to gameplay, to where I then consulted Claude. I did not understand how this project step wanted me to turn in the information and element design of this project and was overwhelmed by how much I wanted to detail. So I asked claude to break it down step by step into creating this document so that I could think through how I wanted each detail. Under NO circumstance did I offload any critical thinking while partnering with Claude on this step. I asked Claude: “Help me make a Development Plan by answering these questions. After this session, I want to have a nicely formatted paper I can turn into my teacher. Just run me through the questions, and challenge my responses if they are not robust enough.” I then copy and pasted the development plan questions into Claude and Claude brought me through them 1 by one. The last part of my query, challenging my responses if they are not robust enough, was critical to the production value of my teaming with Claude. By challenging my design decisions with edge cases that I considered but did not explicitly say, Claude guided me towards creating a more robust and worthwhile project description and plan. Claude helped reframe my goals for this project development into boolean, gradable, there or not states. By reframing my goals into these more straightforward bullets, I was able to understand what I wanted to deliver on a deeper level and be able to communicate it as such better. Claude then helped me flesh out my explicit and implicit features. It recommended that I write out an imagined gameplay example. I wrote: 

“Game play:

Game launches  
Screen loads. 1 player on top, 1 player on bottom  
After 5 seconds of waiting, player 1 parchment loads  
Player 1 draws spell. Then hits cast.  
Player 1 hands device off to player 2\.  
Player 2 draws spell. Then hits cast.  
Game decides accuracy of spells based on templates.  
Game casts most accurate spell each players drawing looks like (if accuracy is above 50%)  
Game runs through decision tree. 

This is the decision tree:

Fire vs Wind vs Earth

Fire: Beats Earth, Loses to Wind  
Attack: Win \= 1x dmg, Lose \= 0.5 dmg  
Block: Win \= 0x dmg, Lose \= 0.5 dmg  
Heal: Win \= 2 HP, Lose \= 0 HP

Wind: Beats Fire, Loses to Earth  
Attack: Win \= 1x dmg, Lose \= 0.5 dmg  
Block: Win \= 0x dmg, Lose \= 0.5 dmg  
Heal: Win \= 2 HP, Lose \= 0 HP

Earth: Beats Wind, Loses to Fire  
Attack: Win \= 1x dmg, Lose \= 0.5 dmg  
Block: Win \= 0x dmg, Lose \= 0.5 dmg  
Heal: Win \= 2 HP, Lose \= 0 HP

HP totals are calculated after receiving damage or healing.  
Next round begins.  
Players play until 1 player reaches 0 HP. If both players reach 0 HP at the same turn, whoevers drawings were most accurate wins”

By writing out my gameplay as such, I was able to break it down into features. Then with each feature I was able to break it down into explicit and implicit (front end and back end) features. For example, Claude challenged my conceptual ideas and the functions I wanted to use to calculate HP changes and helped me reevaluate how I wanted to flesh out the healing mechanic. Claude would list my shortcomings in the description as “Gaps”, and created suggestions for closing these gaps. I never explicitly took the entirety of a Gap closer, rather I just used my own intuition and common sense factoring in what Claude recommended as a decision. After fleshing out features, Claude and I fleshed out the code structure, and the classes. This part was the most helpful out of any use with Claude. My bottom line goal for this project is to expand my understanding of Python and its capabilities to become more fluent and translate these skills into all domains of computer science. Claude in this conversation in no way compromised this Goal. Rather I was able to bounce ideas off of it on how to structure my code after I already tried jumping in the deep end before having this conversation to flesh out the structure of my code. I evaluated my classes by looking at Nouns in my features. I said to Claude giving it my idea before I looked at its feedback:

“Here is what I want my classes to look like:

Player: needs to remember HP, HP icon, player icon, needs functions that update HP  
Spell: will have 3 sublcasses of each element. Will have base attack, block multiplier, and heal amounts.  
Fire/Wind/Earth: Will have 3 spell types defined as functions. Will have weaknesses and strengths listed, and spell type listed.   
StrokeRecognizer: Will have templates for each spell that needs to be casted. Will store accuracy of spells casted for each player in a game.  
RulesEngine: Will just handle game outcomes based on HP thresholds and accuracy thresholds. Spell interactions will be determined in the spell class. Will store rounds here and checks for winner.  
Arena: Will draw arena. Visual effects of 9 spells will be stored here. screen states will be a subclass that holds handoff, and game end”

Claude then looked at my classes, applied feedback. We decided to no longer have elements as sublcasses as spells because it will be redundant and reuse a lot of code. It really did\! When I wrote it out I thought, “wow, this is stupid. I feel like I shouldn’t need to write this much code.” I will instead treat spells as objects of spell class rather than subclasses. Claude also introduced the idea to me of having a definite class for game states and screens. Claude then helped me understand what I wanted my minimal viable product to be. I said for a minimal viable product, I wanted: 

“I want a playable loop, with a drawing mechanic, but not a fleshed out accuracy system. instead of the game deciding spells on accuracy, the player will just draw and a random spell will be chosen because we can fill that missing logical bridge in later”

Claud refined this idea, and we agreed to also reduce the number of spells in game to 3 instead of 9 to make implementation faster. I also decided to make “Spell visuals and visual polish on the parchment and arena will be the final step”. For the testing plan I originally wanted:

“4 new payers draw each spell 10 times, and get their opinions on the game logic if it makes sense and is a cool idea to them.”

But later refined it to “Four players who have not seen the game will each draw every spell 3 times, for 108 total drawings.” And also to test game made logical sense. In conclusion, Claude wrote this paper for me, but it was entirely my critical thinking. This paper is a reflection of my thought, what I wanted to create, but was polished and refined so that I can write the code myself without the help of AI because I now have such a polished plan. West Point, NY. 9 October 2026\. [https\://claude.ai/share/6ec27264-a7d0-481c-99dc-c010e329cc52](https://claude.ai/share/6ec27264-a7d0-481c-99dc-c010e329cc52).  
