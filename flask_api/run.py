from app import create_app
from app.extensions import db
from app.models import Story, Page, Choice

app = create_app()

def seed_database():
    """Populates the database with initial data."""
    
    # Check if data exists to prevent duplicates
    if Story.query.first():
        print("Database already contains data. Skipping seed.")
        return

    print("Seeding database...")

    # --- STORIES ---
    # We set IDs explicitly to match mock data structure
    story1 = Story(
        id=1,
        title="The Haunted Mansion (16 endings)",
        description="Explore a mysterious mansion and uncover its secrets",
        status="published",
        start_page_id=1
    )
    story2 = Story(
        id=2,
        title="Space Adventure (8 endings)",
        description="Journey through the cosmos",
        status="published",
        start_page_id=501
    )

    # Seed Story 1 base page id
    s1_page_base = 1
    
    # Seed Story 2 base page id
    s2_page_base = 501
    

    # === perfect binary tree structure of pages (nodes) and choices (links) ===

    # --- PAGES ---
    pages = [
        # Story 1 Pages
        Page(
            id=s1_page_base, story_id=1, 
            text="You stand before a dark, ominous mansion. The front door is slightly ajar. What do you do?",
            is_ending=False, ending_label=None
        ),


        Page(
            id=s1_page_base+1, story_id=1, 
            text="You step across the threshold. As the heavy oak door slams shut behind you, the sound echoes like a gunshot through the house. You pull on the handle, but it is locked tight. You are trapped.\n\nThe foyer is immense, lit only by moonlight filtering through high, grime-streaked windows. Dust motes dance in the pale beams. To your left, a grand, carpeted staircase ascends into the darkness of the second floor. Straight ahead, a narrow, shadowy hallway stretches toward the back of the house; the air coming from there smells of damp earth and rot.",
            is_ending=False, ending_label=None
        ),

        # Based on base+1 choice
        Page(
            id=s1_page_base+3, story_id=1, 
            text="You creep up the creaking stairs, clutching the banister. At the top, you find a long corridor lined with oil paintings of severe-looking aristocrats. As you walk, you get the distinct, prickling sensation that the painted eyes are following your movement.\n\nAt the end of the hall, the path splits. To the left is a heavy mahogany door with a brass plaque that reads Master Bedroom. To the right is a set of double doors with frosted glass, likely leading to a Library.",
            is_ending=False, ending_label=None
        ),        
        Page(
            id=s1_page_base+4, story_id=1, 
            text="You choose the ground floor, moving deeper into the house. The temperature drops twenty degrees as you walk down the hall. The silence is broken by a faint, rhythmic thumping sound coming from beneath the floorboards.\n\nYou arrive at a junction. To your left is an archway leading to a lavish Dining Room, where a table is strangely set for dinner. To your right is a heavy iron door that is slightly ajar, leading down to the Basement.",
            is_ending=False, ending_label=None
        ),

        # Based on base+3 choice
        Page(
            id=s1_page_base+5, story_id=1, 
            text="You push open the door to the Master Bedroom. It is a time capsule of Victorian elegance, draped in cobwebs. In the corner, a large wardrobe looms. Opposite the bed sits an ornate vanity table with a large, oval mirror.\n\nSuddenly, you hear a soft weeping sound. It seems to be coming from the mirror itself. The reflection in the glass ripples like water, showing a room that isn't the one you are standing in. However, the wardrobe door rattles violently, as if something is trying to get out—or get in.",
            is_ending=False, ending_label=None
        ),        
        Page(
            id=s1_page_base+6, story_id=1, 
            text="You enter the Library. The smell of old paper and leather is overwhelming. Floor-to-ceiling shelves are packed with rotting books. In the center of the room, a large book lies open on a pedestal, glowing with a faint purple light.\n\nNear the window stands a massive antique globe. As you step closer, the globe begins to spin on its own, faster and faster, until it blurs. The glowing book's pages flip frantically as if caught in a wind that you cannot feel.",
            is_ending=False, ending_label=None
        ),
        
        # Based on base+4 choice
        Page(
            id=s1_page_base+7, story_id=1, 
            text="You step into the Dining Room. The long table is laden with a feast—roast boar, fresh fruits, and goblets of wine—looking perfectly preserved despite the decay of the house. Seated at the head of the table is a skeletal figure dressed in a tuxedo, motionless.\n\nYou realize you are starving. The food smells hypnotic. However, under the table, you spot a trapdoor that seems to lead to a servant's escape tunnel. The skeleton slowly turns its head toward you.",
            is_ending=False, ending_label=None
        ),        
        Page(
            id=s1_page_base+8, story_id=1, 
            text="You descend the stone steps into the dark, damp Basement. The rhythmic thumping becomes a heartbeat. In the center of the room, surrounded by lit black candles, is a pulsating mass of shadow. It is a ritual circle, and the barrier between worlds is thin here.\n\nOn a nearby shelf sits a jar of salt and a silver dagger. The shadow begins to take form, rising to meet you. It whispers promises of power.",
            is_ending=False, ending_label=None
        ),

        # Based on base+5 choice
        Page(
            id=s1_page_base+9, story_id=1, 
            text="You stare into the glass. The reflection reaches out, grabs you by the collar, and pulls. You tumble forward, not hitting glass, but falling into a cold, grey void. You are now the reflection, destined to watch from the other side as the next adventurer enters the bedroom. You are trapped forever.",
            is_ending=True, ending_label="The Mirror"
        ),        
        Page(
            id=s1_page_base+10, story_id=1, 
            text="You rip open the wardrobe doors. A swarm of bats explodes outward, blinding you. In the chaos, you stumble backward and trip over a loose floorboard. Beneath it, you find a golden key and a deed to the house. The ghosts, recognizing the new owner, fade away. You survive and are now the wealthy owner of a (mostly) renovated mansion.",
            is_ending=True, ending_label="The Wardrobe"
        ),

        # Based on base+6 choice
        Page(
            id=s1_page_base+11, story_id=1, 
            text="You read the incantation aloud. The purple light surges, filling your vision. You feel your body dissolving, turning into pure thought. You have become the new Librarian, an ethereal spirit bound to the books, possessing infinite knowledge but no voice to share it. You are now a guardian of the library.",
            is_ending=True, ending_label="The Book"
        ),        
        Page(
            id=s1_page_base+12, story_id=1, 
            text="You grab the globe to stop it. It halts instantly, and a secret door in the bookshelf swings open. Sunlight pours in—it’s a hidden exit leading to the garden! You scramble out, breathing the fresh night air. You run until your lungs burn, never looking back. You escaped, but you'll never sleep without a light on again.",
            is_ending=True, ending_label="The Globe"
        ),

        # Based on base+7 choice
        Page(
            id=s1_page_base+13, story_id=1, 
            text="You take a bite of the fruit. It turns to ash in your mouth. The skeleton stands and raises a toast. As you choke, you feel your skin withering, your flesh drying up. You take your seat at the table, a new permanent guest at the eternal dinner party. You have joined the banquet of the dead.",
            is_ending=True, ending_label="The Feast"
        ),        
        Page(
            id=s1_page_base+14, story_id=1, 
            text="You dive under the table and yank open the hatch. You slide down a chute, landing in a pile of hay outside the mansion grounds. You are covered in grime and bruises, but you are alive. As you walk away, the mansion’s lights flick off, one by one, as if disappointment has set in. You survived by the skin of your teeth.",
            is_ending=True, ending_label="The Trapdoor"
        ),

        # Based on base+8 choice
        Page(
            id=s1_page_base+15, story_id=1, 
            text="You scatter the salt and plunge the dagger into the floor. A deafening shriek tears through the air as the shadow dissipates. The house groans, the oppression lifting instantly. The heavy front door upstairs clicks unlocked. You walk out the front door, the hero who cleansed the house. You are a victorious paranormal investigator.",
            is_ending=True, ending_label="The Breaker"
        ),        
        Page(
            id=s1_page_base+16, story_id=1, 
            text="You step into the circle. The shadows embrace you, entering your veins like ice water. You do not die; you change. Your eyes turn pitch black. You are no longer human, but a vessel for the ancient entity. You walk back upstairs; you have no desire to leave. This is your house now. You have become the monster.",
            is_ending=True, ending_label="The Power"
        ),



        Page(
            id=s1_page_base+2, story_id=1, 
            text="You turn your back on the mansion, deciding that some secrets are better left unsolved. You head toward the iron gates, but as you walk, a thick, unnatural fog rolls in from the surrounding woods. It swallows the mansion behind you and obscures the road ahead.\n\nYou reach your car, which is parked just outside the gates. You turn the key in the ignition. The engine coughs, sputters, and dies. The battery is dead. Suddenly, you hear the crunch of dry leaves—footsteps—coming from the tree line.",
            is_ending=False, ending_label=None
        ),        

        # Based on base+2 choice
        Page(
            id=s1_page_base+17, story_id=1, 
            text="You lock the doors and recline the seat, hoping to stay hidden. The footsteps stop right beside your door. A heavy silence hangs in the air, broken only by your own rapid heartbeat.\n\nA hand slaps against the driver's side window, leaving a muddy print. You look up to see a figure in a tattered mechanic’s jumpsuit. He isn't looking at you; he is looking past you, toward the windshield. He screams, \"It's on the roof!\"",
            is_ending=False, ending_label=None
        ),
        Page(
            id=s1_page_base+18, story_id=1, 
            text="You sprint into the dense treeline. The fog is thinner here, but the trees are ancient and twisted, their branches interlocking like skeletal fingers. You realize quickly that you have lost your sense of direction.\n\nYou stumble upon a small clearing. In the center stands a crumbling stone well emitting a faint blue glow. To your right, a narrow dirt path winds toward a distant, flickering light that looks like a cabin.",
            is_ending=False, ending_label=None
        ),

        # Based on base+17 choice
        Page(
            id=s1_page_base+19, story_id=1, 
            text="You unlock the door. The mechanic dives into the passenger seat just as a massive, clawed hand smashes through the sunroof, tearing the upholstery where his head was a second ago. The car rocks violently.\n\nThe mechanic shouts that he has a flare gun in his pocket but dropped a shell on the floor mat. The creature on the roof is tearing the metal roof open like a sardine can",
            is_ending=False, ending_label=None
        ),
        Page(
            id=s1_page_base+20, story_id=1, 
            text="You slam your hand on the horn. The blaring sound cuts through the night. The figure outside recoils, covering his ears, and runs off into the dark. The weight on the roof lifts as something leaps off and chases the mechanic.\n\nYou are alone again. The silence returns, but now the radio flickers to life on its own. A static-filled voice begins reciting a sequence of numbers that sound like coordinates.",
            is_ending=False, ending_label=None
        ),

        # Based on base+18 choice
        Page(
            id=s1_page_base+21, story_id=1, 
            text="You approach the well. The blue glow is hypnotic. As you lean over the edge, the water below doesn't reflect your face; instead, it shows the night sky, but the stars are different—foreign constellations.\n\nA voice echoes up from the depths, sounding exactly like your own voice, asking for a hand up. The ground around the well begins to crumble under your feet.",
            is_ending=False, ending_label=None
        ),
        Page(
            id=s1_page_base+22, story_id=1, 
            text="You reach the cabin. It is a small, wooden shack adorned with bundles of drying herbs and bones hanging from the porch. The door is open. Inside, an old woman sits by a fire, knitting with what looks like silver hair.\n\nShe doesn't look up, but she speaks to you: \"You have left the path of the dead (the mansion) only to enter the domain of the lost. I can offer you a trade: your memory for your safety.\"",
            is_ending=False, ending_label=None
        ),
        
        # Based on base+19 choice
        Page(
            id=s1_page_base+23, story_id=1, 
            text="You fumble in the dark and find the shell. The mechanic loads it and fires upward through the shattered roof. The magnesium flare ignites inside the creature's chest. It shrieks and falls off the car, burning. The car catches fire, but you both scramble out. The mechanic nods at you, a bond forged in fire. You survived the night, but you'll have to walk home.",
            is_ending=True, ending_label="The Flare"
        ),
        Page(
            id=s1_page_base+24, story_id=1, 
            text="You fumble in the dark and find the shell. The mechanic loads it and fires upward through the shattered roof. The magnesium flare ignites inside the creature's chest. It shrieks and falls off the car, burning. The car catches fire, but you both scramble out. The mechanic nods at you, a bond forged in fire. You survived the night, but you'll have to walk home.",
            is_ending=True, ending_label="The Run"
        ),

        # Based on base+20 choice
        Page(
            id=s1_page_base+25, story_id=1, 
            text="You map the coordinates. They point to the exact spot where your car is parked. Suddenly, the GPS voice says, \"You have arrived.\" The car locks engage automatically. The fog fills the interior of the vehicle, smelling of sulfur. You are not on a road anymore. You have been abducted.",
            is_ending=True, ending_label="The Coordinates"
        ),
        Page(
            id=s1_page_base+26, story_id=1, 
            text="You punch the radio display, shattering the plastic. The voice stops, but the electronics spark and ignite the dashboard. The fire spreads instantly to the fuel line. You scramble out just as the car explodes. The explosion attracts the police, who find you dazed on the road. You are safe, though you have some explaining to do to your insurance company.",
            is_ending=True, ending_label="The Radio"
        ),

        # Based on base+21 choice
        Page(
            id=s1_page_base+27, story_id=1, 
            text="You map the coordinates. They point to the exact spot where your car is parked. Suddenly, the GPS voice says, \"You have arrived.\" The car locks engage automatically. The fog fills the interior of the vehicle, smelling of sulfur. You are not on a road anymore. You have been abducted.",
            is_ending=True, ending_label="The Reach"
        ),
        Page(
            id=s1_page_base+28, story_id=1, 
            text="You punch the radio display, shattering the plastic. The voice stops, but the electronics spark and ignite the dashboard. The fire spreads instantly to the fuel line. You scramble out just as the car explodes. The explosion attracts the police, who find you dazed on the road. You are safe, though you have some explaining to do to your insurance company.",
            is_ending=True, ending_label="The Rock"
        ),

        # Based on base+22 choice
        Page(
            id=s1_page_base+29, story_id=1, 
            text="You nod. The woman snaps her fingers. You blink, and suddenly you are sitting in your living room, drinking tea. You feel happy and safe. You have no idea how you got there, or why there is mud on your shoes. You don't remember the mansion. You don't remember your name. You are safe, blissfully ignorant and empty.",
            is_ending=True, ending_label="The Trade"
        ),
        Page(
            id=s1_page_base+30, story_id=1, 
            text="You step back. The woman stops knitting and points a needle at you. \"Then you remain lost,\" she hisses. The cabin door slams shut in your face. When you turn around, the forest is gone. You are standing in the mansion's foyer. All roads lead back to the house. Your adventure has looped; there is no escape.",
            is_ending=True, ending_label="The Refusal"
        ),

        ##################################################################################################################################################################################################################

        # Story 2 Pages
        Page(
            id=s2_page_base, story_id=2, 
            text="Your spaceship is ready. Do you explore the asteroid field or head to the planet?",
            is_ending=False, ending_label=None
        ),

        # Based on base+0 choice
        Page(
            id=s2_page_base+1, story_id=2, 
            text="You steer your ship, the Star-Hopper, into the dense asteroid field. Rocks the size of mountains drift silently past your cockpit. Suddenly, your proximity alarm screams.\n\nTo your starboard side, sensors detect a faint, rhythmic distress signal emanating from a derelict freighter drifting near a volatile gas cloud. To your port side, deep scanners reveal a massive, hollowed-out asteroid emitting high-energy readings—likely a hidden mining operation or a pirate hideout.",
            is_ending=False, ending_label=None
        ),
        Page(
            id=s2_page_base+2, story_id=2, 
            text="You engage thrusters and descend toward the planet Xylos. The atmosphere is a swirling mix of purple and gold clouds. As you break through the cloud layer, two distinct landing zones become visible.\n\nAbove the clouds hovers a gleaming, silver metropolis kept aloft by anti-gravity engines. Below, on the surface, lies a bioluminescent jungle that pulses with a strange, organic light.",
            is_ending=False, ending_label=None
        ),

        # Based on base+1 choice
        Page(
            id=s2_page_base+3, story_id=2, 
            text="You dock with the freighter. The airlock hisses open, revealing a dark corridor floating in zero-gravity. Debris floats everywhere. You make your way to the bridge and find the crew is gone, but the ship's logs are active.\n\nThe log mentions a \"cargo\" that drove the crew to madness. In the cargo hold, you find a containment unit humming with unstable energy. Beside it is the ship's self-destruct mechanism, which has been armed but paused with 10 seconds on the clock.",
            is_ending=False, ending_label=None
        ),
        Page(
            id=s2_page_base+4, story_id=2, 
            text="You fly into the hollow asteroid. Inside is a bustle of activity—ships are being stripped for parts by rough-looking aliens. This is a Scavenger Hive.\n\nA tractor beam locks onto your ship, dragging you in. The Scavenger King, a four-armed cyborg, hails you on the video screen. He offers you a choice: join his fleet for a dangerous raid, or try to win your freedom by racing his champion through the \"Tunnel of Razors.\"",
            is_ending=False, ending_label=None
        ),

        # Based on base+2 choice
        Page(
            id=s2_page_base+5, story_id=2, 
            text="You land on a pristine platform. The city is inhabited entirely by synthetics—robots of all shapes and sizes. A towering droid approaches you. It scans your biological signature and pauses.\n\n\"Organics are forbidden here unless they undergo the Integration,\" the droid says mechanically. \"Submit to the upgrade, or prove your intellectual worth in the Logic Court.\"",
            is_ending=False, ending_label=None
        ),
        Page(
            id=s2_page_base+6, story_id=2, 
            text="You touch down in the jungle. The plants here are massive, and they seem to turn toward you as you walk. You discover a stone ruin covered in vines that glow rhythmically.\n\nIn the center of the ruin is a pool of silver liquid. A small, furry creature—a local native—gestures for you to drink from it. Meanwhile, your scanner detects a rare mineral deposit under the roots of a nearby tree that could make you rich, but extracting it might hurt the forest.",
            is_ending=False, ending_label=None
        ),

        # Based on base+3 choice
        Page(
            id=s2_page_base+7, story_id=2, 
            text="You try to stabilize the container. You fail. The containment field collapses, releasing a microscopic singularity. The black hole expands instantly, swallowing the freighter and your ship in a blink of an eye. You have been crushed into infinite density.",
            is_ending=True, ending_label="Steal Cargo"
        ),
        Page(
            id=s2_page_base+8, story_id=2, 
            text="You hit the eject button and scramble back to your ship. The freighter explodes behind you, the shockwave propelling you forward. You check your sensors and realize the explosion cleared a path through the asteroid field, revealing a hyper-lane shortcut. You survived and shaved two weeks off your journey.",
            is_ending=True, ending_label="Eject Cargo"
        ),

        # Based on base+4 choice
        Page(
            id=s2_page_base+9, story_id=2, 
            text="You join the Scavengers. The raid is a success, and you earn a fortune in stolen credits. However, you are now a wanted criminal in three systems. You paint your ship black and embrace the outlaw life. You are now a dreaded Space Pirate.",
            is_ending=True, ending_label="The Raid"
        ),
        Page(
            id=s2_page_base+10, story_id=2, 
            text="You rev your engines and speed into the razor tunnel. The champion is fast, but reckless. He clips a jagged rock and spins out. You boost past him, breaking the sound barrier and exiting the asteroid into open space. The Scavengers respect the win and let you go. You are free, and you have a great story for the cantina.",
            is_ending=True, ending_label="The Race"
        ),

        # Based on base+5 choice
        Page(
            id=s2_page_base+11, story_id=2, 
            text="You agree to the upgrade. Nano-machines enter your bloodstream. Your fear vanishes, replaced by cold calculation. You realize that organic life is inefficient. You park your ship permanently and plug into the mainframe. You are no longer human; you are part of the System.",
            is_ending=True, ending_label="Integration"
        ),
        Page(
            id=s2_page_base+12, story_id=2, 
            text="You stand before the High Processor. You present a paradox: \"This statement is false.\" The robots freeze, their processors overheating as they try to resolve the loop. The city's defenses shut down. You loot their data archives for valuable tech blueprints and fly away rich. You outsmarted the machines.",
            is_ending=True, ending_label="Logic Trial"
        ),

        # Based on base+6 choice
        Page(
            id=s2_page_base+13, story_id=2, 
            text="You drink the liquid. Your vision shifts. You can see the connections between all living things on the planet. You realize you can speak to the trees. You decide to leave your ship behind and live in the jungle as a shaman. You have found inner peace and a new home.",
            is_ending=True, ending_label="Silver Pool"
        ),
        Page(
            id=s2_page_base+14, story_id=2, 
            text="You fire the laser. The ground screams. The \"trees\" are actually limbs of a planetary super-organism, and you just hurt it. Vines erupt from the ground, crushing your ship and wrapping around your ankles. The planet begins to digest you. Nature fought back, and nature won.",
            is_ending=True, ending_label="Mining Laser"
        ),
    ]

    # Seed Story 1 base choice id
    s1_choice_base = 0
    
    # Seed Story 2 base choice id
    s2_choice_base = 1000
    

    # --- CHOICES ---
    choices = [
        # Haunted Mansion
        # from base+0
        Choice(id=s1_choice_base+1, page_id=s1_page_base, text="Enter the mansion", next_page_id=s1_page_base+2),
        Choice(id=s1_choice_base+2, page_id=s1_page_base, text="Walk away", next_page_id=s1_page_base+3),

        # from base+1
        Choice(id=s1_choice_base+3, page_id=s1_page_base+1, text="Ascend the Grand Staircase.", next_page_id=s1_page_base+4),
        Choice(id=s1_choice_base+4, page_id=s1_page_base+1, text="Walk down the Shadowy Hallway.", next_page_id=s1_page_base+5),

        # from base+3
        Choice(id=s1_choice_base+5, page_id=s1_page_base+3, text="Enter the Master Bedroom.", next_page_id=s1_page_base+6),
        Choice(id=s1_choice_base+6, page_id=s1_page_base+3, text="Enter the Library.", next_page_id=s1_page_base+7),

        # from base+4
        Choice(id=s1_choice_base+7, page_id=s1_page_base+4, text="Enter the Dining Room.", next_page_id=s1_page_base+8),
        Choice(id=s1_choice_base+8, page_id=s1_page_base+4, text="Descend into the Basement.", next_page_id=s1_page_base+9),

        # from base+5
        Choice(id=s1_choice_base+9, page_id=s1_page_base+5, text="Gaze into the Vanity Mirror to investigate the image.", next_page_id=s1_page_base+10),
        Choice(id=s1_choice_base+10, page_id=s1_page_base+5, text="Throw open the Wardrobe to confront the noise.", next_page_id=s1_page_base+11),        

        # from base+6
        Choice(id=s1_choice_base+11, page_id=s1_page_base+6, text="Read the glowing book.", next_page_id=s1_page_base+12),
        Choice(id=s1_choice_base+12, page_id=s1_page_base+6, text="Stop the spinning globe.", next_page_id=s1_page_base+13),        

        # from base+7
        Choice(id=s1_choice_base+13, page_id=s1_page_base+7, text="Sit down and partake in the feast.", next_page_id=s1_page_base+14),
        Choice(id=s1_choice_base+14, page_id=s1_page_base+7, text="Dive for the trapdoor under the table.", next_page_id=s1_page_base+15),     

        # from base+8
        Choice(id=s1_choice_base+15, page_id=s1_page_base+8, text="Use the salt and dagger to break the ritual.", next_page_id=s1_page_base+16),
        Choice(id=s1_choice_base+16, page_id=s1_page_base+8, text="Step into the circle to accept the power.", next_page_id=s1_page_base+17),  


        # from base+2
        Choice(id=s1_choice_base+17, page_id=s1_page_base+2, text="Stay in the car and lock the doors.", next_page_id=s1_page_base+18),
        Choice(id=s1_choice_base+18, page_id=s1_page_base+2, text="Get out and run into the woods to hide.", next_page_id=s1_page_base+19),

        # from base+17
        Choice(id=s1_choice_base+19, page_id=s1_page_base+17, text="Unlock the door to let the mechanic in.", next_page_id=s1_page_base+20),
        Choice(id=s1_choice_base+20, page_id=s1_page_base+17, text="Honk the horn to scare them both away.", next_page_id=s1_page_base+21),

        # from base+18
        Choice(id=s1_choice_base+21, page_id=s1_page_base+18, text="Investigate the glowing well.", next_page_id=s1_page_base+22),
        Choice(id=s1_choice_base+22, page_id=s1_page_base+18, text="Head toward the cabin light.", next_page_id=s1_page_base+23),

        # from base+19
        Choice(id=s1_choice_base+23, page_id=s1_page_base+19, text="Help him search for the flare shell.", next_page_id=s1_page_base+24),
        Choice(id=s1_choice_base+24, page_id=s1_page_base+19, text="Kick the door open and make a run for it together.", next_page_id=s1_page_base+25),

        # from base+20
        Choice(id=s1_choice_base+25, page_id=s1_page_base+20, text="Write down the coordinates and try to find them on your phone map.", next_page_id=s1_page_base+26),
        Choice(id=s1_choice_base+26, page_id=s1_page_base+20, text="Smash the radio to stop the voice.", next_page_id=s1_page_base+27),

        # from base+21
        Choice(id=s1_choice_base+27, page_id=s1_page_base+21, text="Reach down to help the figure.", next_page_id=s1_page_base+28),
        Choice(id=s1_choice_base+28, page_id=s1_page_base+21, text="Throw a rock into the well to break the illusion.", next_page_id=s1_page_base+29),

        # from base+22
        Choice(id=s1_choice_base+29, page_id=s1_page_base+22, text="Accept the trade.", next_page_id=s1_page_base+30),
        Choice(id=s1_choice_base+30, page_id=s1_page_base+22, text="Refuse and back away slowly.", next_page_id=s1_page_base+31),

        ################################################################################################################################################################
        
        # Space Adventure
        # from base+0
        Choice(id=s2_choice_base+1, page_id=s2_page_base, text="Explore the asteroid field", next_page_id=s2_page_base+1),
        Choice(id=s2_choice_base+2, page_id=s2_page_base, text="Head to the planet", next_page_id=s2_page_base+2),

        # from base+1
        Choice(id=s2_choice_base+3, page_id=s2_page_base+1, text="Investigate the distress signal on the derelict freighter.", next_page_id=s2_page_base+3),
        Choice(id=s2_choice_base+4, page_id=s2_page_base+1, text="approach the hollow asteroid to investigate the energy readings.", next_page_id=s2_page_base+4),

        # from base+2
        Choice(id=s2_choice_base+5, page_id=s2_page_base+2, text="Request permission to dock at the Floating City.", next_page_id=s2_page_base+5),
        Choice(id=s2_choice_base+6, page_id=s2_page_base+2, text="land in a clearing within the Bioluminescent Jungle.", next_page_id=s2_page_base+6),

        # from base+3
        Choice(id=s2_choice_base+7, page_id=s2_page_base+3, text="Attempt to stabilize and steal the cargo.", next_page_id=s2_page_base+7),
        Choice(id=s2_choice_base+8, page_id=s2_page_base+3, text="Eject the cargo into space and flee immediately.", next_page_id=s2_page_base+8),

        # from base+4
        Choice(id=s2_choice_base+9, page_id=s2_page_base+4, text="Agree to join the raid.", next_page_id=s2_page_base+9),
        Choice(id=s2_choice_base+10, page_id=s2_page_base+4, text="Challenge the champion to the race.", next_page_id=s2_page_base+10),

        # from base+5
        Choice(id=s2_choice_base+11, page_id=s2_page_base+5, text="Submit to the Integration upgrade.", next_page_id=s2_page_base+11),
        Choice(id=s2_choice_base+12, page_id=s2_page_base+5, text="Demand a trial by logic.", next_page_id=s2_page_base+12),

        # from base+6
        Choice(id=s2_choice_base+13, page_id=s2_page_base+6, text="Drink from the silver pool.", next_page_id=s2_page_base+13),
        Choice(id=s2_choice_base+14, page_id=s2_page_base+6, text="Ignite your mining laser to harvest the minerals.", next_page_id=s2_page_base+14),

    ]

    # --- COMMIT ---
    # Add everything to the session
    db.session.add(story1)
    db.session.add(story2)
    db.session.add_all(pages)
    db.session.add_all(choices)

    # Commit the transaction
    db.session.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    # Context is required to access the DB
    with app.app_context():
        # Team note: uncomment next line to WIPE and reset the DB every time we restart
        # db.drop_all()
        
        # Create tables if they don't exist (handled by factory in __init__.py, but safe here)
        db.create_all()
        
        # Run seed
        seed_database()

    app.run(debug=True)