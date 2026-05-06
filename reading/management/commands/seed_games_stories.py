import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


STORY_TEXTS = {}


STORY_TEXTS["iniciante"] = [
    (
        "Playing Video Games",
        """I like to play video games every day. I have a computer and a console. My favorite games are about adventures and magic. I use a controller to move the character. Sometimes, I play with my friends online. We talk and help each other in the game. Playing games is very fun and it helps me relax after university.""",
    ),
    (
        "The Game Console",
        """A game console is a machine for video games. You connect the console to the television. There are many brands, like Nintendo, PlayStation, and Xbox. Some consoles are small and you can carry them in your bag. I have a new console in my bedroom. It is fast and the colors are very bright. I love my new console.""",
    ),
    (
        "Mobile Games",
        """Many people play games on their smartphones. These are called mobile games. You can play them on the bus or at the park. Some mobile games are very simple, like puzzles or card games. They are usually free to download. I play a puzzle game on my phone during my break at Americanas. It is a good way to pass the time.""",
    ),
    (
        "The Main Character",
        """In every game, there is a main character. This is the person you control. Some characters are brave warriors, and others are fast animals. You can often change the character's clothes or hair. My favorite character is a space explorer. He travels to different planets and meets aliens. The character is the hero of the story.""",
    ),
    (
        "Winning and Losing",
        """In a game, you can win or lose. When you win, you get points or a trophy. It is a very happy moment. But sometimes, the game is difficult and you lose. When I lose, I don't get sad. I try again and I learn from my mistakes. Games are about practice and patience. To win the final level is a great feeling.""",
    ),
    (
        "Online Friends",
        """I have many friends in my favorite online game. We live in different cities, but we play together every night. We use a headset to talk while we play. We are a team and we work together to win. It is very cool to meet people from different places. Games connect people and create new friendships.""",
    ),
    (
        "Game Graphics",
        """Graphics are the pictures in a video game. Modern games have amazing graphics. The trees, the water, and the people look very real. Some games have pixel art style. This style looks like old games from the 80s. I like both styles. Good graphics make the game world beautiful and interesting to explore.""",
    ),
    (
        "The Game Menu",
        """When you start a game, you see the main menu. In the menu, you can select New Game or Load Game. You can also change the settings, like the sound or the language. I always change my games to English to practice my vocabulary. The menu is very easy to use. I click Start and the adventure begins.""",
    ),
    (
        "Learning with Games",
        """Video games are not just for fun. You can learn many things with games. Some games teach history, science, or a new language. I learn many English words when I play RPG games. You need to read the instructions and talk to other characters. Games are a very interactive way to study and grow.""",
    ),
    (
        "A Professional Gamer",
        """Some people play games for a job. They are called professional gamers or pro players. They practice for many hours every day. They play in big competitions called eSports. Thousands of fans watch these players on the internet. It is a very difficult job, but it is also very exciting. Technology creates new types of careers.""",
    ),
]


STORY_TEXTS["a1"] = [
    (
        "My Gaming Routine",
        """I usually finish my internship at Americanas at 6:00 PM. After that, I go home and play video games for one hour. I often play adventure games because they are very relaxing. Tonight, I am going to try a new RPG called Starlight Odyssey. I am going to create a character with magic powers. I never play horror games at night because they are too scary! My gaming routine helps me to disconnect from my software engineering studies. Tomorrow, I am going to play a multiplayer game with my university friends.""",
    ),
    (
        "Choosing a New Genre",
        """There are many different genres of games. Some people love FPS (First-Person Shooters) because they are fast and exciting. Other people prefer Simulation games, like building a city or a farm. I usually prefer Strategy games because I need to use my brain to solve problems. Next weekend, I am going to explore a different genre. I am going to play a sports game for the first time. I am going to choose a football game and try to win the championship. It is going to be a fun challenge!""",
    ),
    (
        "The Mobile Gaming Trend",
        """Everyone has a smartphone today, so mobile games are very popular. I usually play a simple puzzle game when I am on the bus. It is very convenient because I don't need a console. Next month, a famous company is going to release a mobile version of a classic RPG. Many people are going to download it on the first day. I am going to check the reviews online before I install the game. Mobile games are getting better every year because smartphone technology is advancing very fast.""",
    ),
    (
        "Buying a New Controller",
        """My old game controller is broken, so I need to buy a new one. I usually prefer wireless controllers because they are more comfortable. Tomorrow, I am going to visit a technology store in the mall. I am going to compare the prices of different brands. I want a black controller with extra buttons for my favorite games. If the store has a promotion, I am also going to buy a new headset. My gaming experience is going to be much better with new equipment!""",
    ),
    (
        "Watching Game Streamers",
        """I often watch streamers on Twitch or YouTube. They play famous games and talk to the audience. I like to watch speedruns, where players finish a game very fast. Tonight, my favorite streamer is going to play a new indie game. He is going to show the best secrets and tips. I am going to learn some new tricks for my own gameplay. Sometimes, streamers give gifts to the fans. I am going to participate in the chat and ask a question about the game's difficulty.""",
    ),
    (
        "Studying with Educational Games",
        """I believe that games are great tools for education. I often use a game to practice my English vocabulary. In the game, I need to read the dialogues to finish the mission. Next week, I am going to start a new game about history. It is going to show how people lived in the past. I am going to learn about ancient civilizations while I play. My professor says that interactive games help students to remember information. It is a very smart way to study!""",
    ),
    (
        "Preparing for a Tournament",
        """My friends and I are going to participate in an online tournament next Saturday. We are going to play a popular battle royale game. We usually practice together three times a week. We need to have a good strategy to win against other teams. I am going to be the healer of the group. I am going to help my friends when they lose health. We are going to communicate using a voice app. I hope we are going to win the first prize!""",
    ),
    (
        "The Mystery of the Final Level",
        """I am currently at the last level of a mystery game. The game is very difficult, but the story is amazing. I usually spend a lot of time thinking about the puzzles. Tonight, I am finally going to discover the secret of the mysterious island. I am going to use a map to find the hidden treasure. After I finish this game, I am going to start a new adventure. I am going to write a review of the game on my blog to help other players.""",
    ),
    (
        "Game Updates and Patches",
        """Modern games always have updates. These updates fix bugs and add new content to the story. Today, my favorite game has a very big update. I am going to wait for the download to finish. It is going to take thirty minutes because the file is large. After the update, the game is going to have new characters and maps. I am going to explore the new area with my online team. Developers are always working to make the games better for the fans.""",
    ),
    (
        "A Future in Game Development",
        """I am a software engineering student, so I am interested in how games are made. I am learning Python and Django now. In the future, I am going to study game engines like Unity or Unreal. I want to create my own indie game one day. I am going to write the story and program the mechanics. My game is going to have a beautiful pixel art style. It is a difficult dream, but I am going to work hard to achieve it. Technology is my passion!""",
    ),
]


STORY_TEXTS["a2"] = [
    (
        "My First Handheld Console",
        """When I was ten years old, my parents gave me my first handheld console. It was a small, purple device with a very tiny screen. At that time, it was the coolest thing I ever owned! I played games like Pokemon and Tetris for hours. Compared to my modern smartphone, the graphics were much simpler and the screen didn't have any colors. However, the battery lasted much longer than my phone's battery today. Last week, I found the old console in a box in my attic. I tried to turn it on, and it still worked! The music sounded more robotic than modern game music, but it made me feel very happy. It was a nostalgic trip to my childhood.""",
    ),
    (
        "PC Gaming vs. Console Gaming",
        """I have played on both PCs and consoles since I was a teenager. In my opinion, PC gaming is more versatile than console gaming because you can upgrade the hardware. Last year, I bought a new graphics card, and my games now look more realistic and run faster than before. However, consoles are usually cheaper and easier to set up. My brother prefers his PlayStation because he thinks the controller is more comfortable than a mouse and keyboard. While I am playing a strategy game on my PC, he is usually playing a sports game on the sofa. Both platforms have their advantages, but for a software engineering student, the PC is the most powerful tool for both work and play.""",
    ),
    (
        "The Evolution of Graphics",
        """The graphics in video games have changed more than any other technology in the last thirty years. I remember playing a game in 2010 where the characters looked like blocks. Yesterday, I watched a trailer for a new game, and the water and the faces looked as real as a movie! Modern games use Ray Tracing, which makes the lights and shadows more natural than in older games. This technology requires a more expensive computer, but the visual experience is much more immersive. Even though the graphics are better now, some people still prefer retro games because they think the gameplay was more challenging and creative in the past.""",
    ),
    (
        "A Frustrating Game Over",
        """Last night, I was playing the most difficult level of an adventure game. I was winning, and I was very close to the final boss. Suddenly, while I was jumping over a fire pit, my internet connection failed. I lost all my progress! I felt angrier than a person in a traffic jam. I tried to reconnect for twenty minutes, but it didn't work. Consequently, I decided to stop playing and go to bed. This morning, I tried again and finally finished the level. I realized that online-only games are more frustrating than offline games when the internet is slow. Patience is the most important skill for a gamer!""",
    ),
    (
        "The Most Iconic Game Music",
        """I've listened to many game soundtracks, but the music from The Legend of Zelda is the most beautiful I ever heard. In the past, game music was very simple because the hardware was limited. Now, many games have full orchestras and professional singers. Last month, I went to a concert where they played music from various video games. It was more emotional and powerful than a regular rock concert! While the orchestra was playing, I remembered my favorite missions and characters. I think that music is more important for the atmosphere of a game than the graphics. It makes the digital world feel more alive and real.""",
    ),
    (
        "Playing with a High Latency",
        """Yesterday, I tried to play a competitive shooter with my friends, but my ping was very high. In gaming, high latency is worse than bad graphics! While I was trying to move, my character was teleporting around the map. I was slower than the other players, so I lost every match. My friends were laughing at me because I was playing so badly. I realized that my router was too far from my bedroom. Today, I bought a long cable to connect my PC directly to the internet. The connection is now more stable and faster than before. Playing with a good connection is much more satisfying!""",
    ),
    (
        "A Classic RPG Adventure",
        """Two years ago, I started playing a classic RPG called Final Fantasy VII. It is older than me, but many people say it is the best game of the genre. At first, the controls were more difficult to use than modern games. However, after a few hours, I fell in love with the story. The characters were more interesting and the world was larger than in many new games. While I was playing, I realized that a good story is more important than perfect graphics. I've already recommended this game to all my university friends. It was a more profound experience than watching a blockbuster movie.""",
    ),
    (
        "The Rise of Cozy Games",
        """Recently, I've started playing more cozy games like Stardew Valley and Animal Crossing. In these games, you don't fight monsters; you just plant flowers, talk to neighbors, and decorate your house. Compared to competitive games, cozy games are much more relaxing and less stressful. I usually play them at night because they help me sleep better. Last week, I built a small digital farm with my cousin. It was the most peaceful afternoon of the month. I think that today, many people prefer these games because our real lives are too busy and noisy. A quiet game is the best medicine for a tired mind.""",
    ),
    (
        "Upgrading My Gaming Setup",
        """Last weekend, I decided to organize my gaming desk. I bought a larger monitor and a more ergonomic chair. My old chair was less comfortable than a wooden bench! Now, my back feels better when I am studying or playing for a long time. I also added some LED lights behind my monitor. My brother says my room looks more like a spaceship than a bedroom now! I think that a better setup makes me more productive and happy. Compared to my old desk, this new space is much more organized and professional. It was the most expensive project of the semester, but it was worth it.""",
    ),
    (
        "Remembering the Arcade Era",
        """When my father was young, he didn't have a console at home. He usually went to Arcades to play games with his friends. He says that the atmosphere was more social and exciting than playing alone in a room. Last month, we visited a Retro Arcade in the city center. I played Pac-Man and Space Invaders on the original machines. They were harder than I thought! You had to be very fast and precise. My father was still better at those games than me. Even though modern games are more complex, those old arcade games were the most addictive and fun experiences of their time.""",
    ),
]


STORY_TEXTS["b1"] = [
    (
        "The Rise of eSports as a Global Phenomenon",
        """Video games have evolved from a simple hobby into a professional competitive field known as eSports. Nowadays, professional players train for many hours a day, just like traditional athletes. Consequently, major tournaments now fill huge stadiums and attract millions of viewers online. In my opinion, eSports should be recognized as real sports because they require intense concentration, quick reflexes, and teamwork. Furthermore, the industry creates many jobs for coaches, commentators, and software engineers. However, some critics argue that sitting in front of a screen is not a healthy activity. I believe that if players maintain a balance between physical exercise and gaming, eSports can be a positive influence. Therefore, as technology continues to advance, the popularity of competitive gaming will likely grow even more, becoming a central part of modern culture.""",
    ),
    (
        "The Controversy of Microtransactions",
        """One of the most debated topics in the gaming industry today is the use of microtransactions. Many free-to-play games allow players to download the game for free, but they charge money for extra items, such as skins or loot boxes. While this model allows more people to try the game, it also has a significant downside. Some games are accused of being pay-to-win, which means that players who spend more money have an unfair advantage over those who do not. Consequently, this can ruin the competitive balance of the game. In my view, microtransactions are acceptable if they are only for cosmetic items. However, if a game encourages gambling behaviors, especially among children, it should be strictly regulated. Therefore, developers must find a balance between making a profit and keeping the game fair and fun for everyone.""",
    ),
    (
        "Virtual Reality: The Future of Immersion?",
        """Virtual Reality (VR) has the potential to completely change how we experience digital worlds. When you wear a VR headset, you are no longer just looking at a screen; you are inside the game. This technology creates a level of immersion that was previously impossible. For instance, if you are playing a horror game in VR, the experience is much more intense and terrifying. Furthermore, VR is not only for gaming; it is also used for training doctors and pilots. However, the hardware is still quite expensive and some people feel motion sickness after playing for a long time. In my opinion, if the technology becomes cheaper and more comfortable, VR will become the standard for home entertainment. Therefore, we are only at the beginning of what this incredible technology can achieve in the future.""",
    ),
    (
        "The Social Impact of Online Communities",
        """Online gaming is often criticized for being isolating, but for many people, it is actually a very social experience. Through platforms like Discord, players can join communities with people who share the same interests. Consequently, they can make friends from all over the world. In my view, these communities provide a sense of belonging, especially for people who feel lonely in their real lives. However, there is also a dark side to online gaming, such as toxicity and bullying. If a player is constantly being insulted by others, they might stop playing altogether. Therefore, it is important for game companies to implement better moderation tools to protect their players. If we foster a culture of respect, online games can be a wonderful place for global friendship and collaboration.""",
    ),
    (
        "Gaming and Mental Health: A Double-Edged Sword",
        """The relationship between video games and mental health is complex. On one hand, games can be a great way to relieve stress and improve cognitive skills, such as problem-solving and spatial awareness. For example, many people played cozy games during the pandemic to feel less anxious. On the other hand, excessive gaming can lead to addiction and social withdrawal. Consequently, the World Health Organization now recognizes gaming disorder as a real condition. In my opinion, moderation is the key. If you use games as a way to relax after a long day of studying software engineering, it is very beneficial. But if you start ignoring your sleep and your responsibilities, it becomes a problem. Therefore, we should educate players about how to enjoy their hobby in a healthy and balanced way.""",
    ),
    (
        "The Impact of Indie Games on Creativity",
        """In the past, the gaming market was dominated by large companies with huge budgets. However, in recent years, indie games created by small teams or even single individuals have become incredibly popular. Games like Undertale or Hollow Knight show that you don't need a lot of money to create a masterpiece. In my view, indie developers are more willing to take risks and try new ideas than big studios. Consequently, they often create more unique and emotional experiences for the players. Furthermore, tools like Unity and Unreal Engine make it easier for students to start their own projects. If you have a good story and a solid game mechanic, you can find success in the modern market. Therefore, the rise of indie games is a victory for creativity and diversity in art.""",
    ),
    (
        "Game Accessibility: Gaming for Everyone",
        """Accessibility in gaming means creating features that allow people with disabilities to enjoy video games. This includes things like customizable controls, subtitles for the deaf, and high-contrast modes for players with low vision. In recent years, companies like Microsoft and Sony have made a lot of progress in this area. For instance, the Xbox Adaptive Controller is designed specifically for players with limited mobility. In my opinion, everyone should have the right to play, regardless of their physical condition. Consequently, when developers prioritize accessibility, they reach a much larger audience. Furthermore, these features often benefit all players, not just those with disabilities. Therefore, making games more inclusive is not only the right thing to do, but it also makes the industry stronger and more diverse.""",
    ),
    (
        "The Environmental Cost of the Gaming Industry",
        """While we often think of gaming as a digital hobby, it has a real impact on the environment. The production of consoles and high-end graphics cards requires rare minerals and a lot of energy. Furthermore, the massive servers used for cloud gaming and online multiplayer consume a significant amount of electricity. Consequently, the carbon footprint of the gaming industry is larger than many people realize. In my view, companies should be more transparent about their environmental impact. If they used more recycled materials and invested in renewable energy, the industry would be much more sustainable. Therefore, as gamers, we should also be conscious of our energy consumption. For example, we can turn off our consoles when we are not using them or choose to buy digital games to reduce plastic waste.""",
    ),
    (
        "Can Video Games Be Considered Art?",
        """For a long time, video games were seen as toys for children. However, many people now argue that games are a sophisticated form of art. Like movies and literature, games tell complex stories and explore deep human emotions. But unlike other art forms, games are interactive. This means that the player is part of the story, and their choices can change the outcome. In my opinion, this interactivity makes the emotional impact even stronger. For example, games like The Last of Us have made many players cry because of their powerful narrative. Furthermore, the combination of music, visual art, and programming creates a unique aesthetic experience. Therefore, video games are the complete art form of the 21st century, combining technology and creativity in a way that no other medium can.""",
    ),
    (
        "The Evolution of Artificial Intelligence in Games",
        """Artificial Intelligence (AI) has always been a part of video games, but it is becoming much more advanced. In the past, enemies followed simple patterns that were easy to predict. Today, however, AI can learn from the player's behavior and adapt its strategy. Consequently, the games become much more challenging and realistic. In my view, this is very exciting for the future of gaming. For instance, we might soon have NPC (Non-Player Characters) that can have natural conversations with us using AI language models. Furthermore, AI is also helping developers to create huge, detailed worlds more quickly. As a software engineering student, I think that studying AI in games is one of the most interesting fields of technology. Therefore, the intelligence of the characters we meet in games will soon be indistinguishable from real people.""",
    ),
]


STORY_TEXTS["b2"] = [
    (
        "The Philosophy of Level Design",
        """Level design is often described as the invisible hand that guides a player through a digital world without stripping them of their agency. In modern masterpieces, the environment itself communicates the objectives; for instance, the clever use of lighting and architecture can subtly direct a player toward a hidden path. This environmental storytelling allows developers to build complex worlds where the history of a location is told through debris, posters, and ruins rather than just dialogue. Consequently, a well-designed level feels like a living space rather than a series of obstacles. In my opinion, the mark of a great level designer is the ability to balance challenge and intuition. If a player feels smart for solving a puzzle, it is usually because the designer laid the groundwork perfectly. As games move toward more open worlds, this craft becomes increasingly essential to maintain narrative focus.""",
    ),
    (
        "Procedural Generation: The Infinite Universe",
        """Procedural generation is a technique where algorithms are used to create game content-such as landscapes, dungeons, or entire galaxies-automatically rather than manually. Games like No Man's Sky utilize this to create billions of unique planets, ensuring that no two players have the exact same experience. The nuance of this technology lies in the mathematical randomness that must be constrained by rules to ensure the content remains playable and interesting. Consequently, it allows small indie teams to create massive worlds that would normally require hundreds of artists. However, some critics argue that procedurally generated content can feel repetitive or lack the soul of hand-crafted levels. In my view, the future of game development lies in a hybrid approach: using AI to handle the vast, repetitive tasks while human designers focus on the critical narrative emotional beats.""",
    ),
    (
        "The Psychological Mechanics of Engagement",
        """Modern game development has increasingly integrated principles of behavioral psychology to maximize player engagement. Concepts like the flow state-where a player is so immersed that they lose track of time-are carefully engineered by balancing the game's difficulty with the player's skill level. If a game is too hard, the player becomes frustrated; if it is too easy, they become bored. Furthermore, many mobile games utilize variable ratio schedules of reinforcement, similar to slot machines, to keep users returning daily. This has sparked an ethical debate regarding the line between fun and addiction. In my opinion, developers have a moral responsibility to ensure that their engagement mechanics do not become exploitative. If the primary goal of a game is to trigger a dopamine loop rather than provide a meaningful experience, it ceases to be art and becomes a mere tool for data harvesting.""",
    ),
    (
        "The Cultural Legacy of the Soulslike Genre",
        """Since the release of Dark Souls in 2011, a new sub-genre known as Soulslike has emerged, characterized by high difficulty, cryptic lore, and a focus on player perseverance. Unlike traditional blockbusters that often hand-hold the player, these games treat failure as a fundamental part of the learning process. Consequently, the satisfaction of overcoming a difficult boss is much higher than in easier titles. The nuance of the genre is its environmental narrative, where players must piece together the story from item descriptions and world details. In my view, the success of these games reflects a desire among players for more challenging and rewarding experiences. It proves that there is a significant market for games that respect the player's intelligence and refuse to simplify their mechanics for the sake of mass appeal.""",
    ),
    (
        "Virtual Economies and the Real-World Value of Digital Goods",
        """Many online games, particularly MMORPGs like EVE Online or World of Warcraft, have complex internal economies that mirror real-world financial systems. Players trade resources, manufacture goods, and even engage in corporate espionage. The nuance of these virtual markets is that they often develop real-world value; rare items can be sold for thousands of dollars on external sites. Consequently, some economists study these games to understand human behavior and market fluctuations in a controlled environment. However, this also leads to problems like gold farming, where workers in low-income countries are paid to perform repetitive tasks to sell digital currency. In my opinion, the fusion of virtual and real economies is inevitable, but it requires robust regulation to prevent fraud and money laundering within gaming platforms.""",
    ),
    (
        "The Ludo-Narrative Dissonance Dilemma",
        """Ludo-narrative dissonance occurs when there is a conflict between a game's story and its gameplay mechanics. A famous example is a protagonist who is portrayed as kind and empathetic in cutscenes but becomes a ruthless killer during gameplay. This disconnect can break a player's immersion and make the story feel inauthentic. Consequently, modern developers are striving for narrative harmony, where the actions the player takes reinforce the character's personality and the game's themes. In my view, this is the greatest challenge in interactive storytelling. If the gameplay does not reflect the narrative, the emotional impact is significantly weakened. Therefore, the most successful games are those where the doing and the telling are perfectly aligned, creating a cohesive and believable experience for the player.""",
    ),
    (
        "The Evolution of Game Engines: Unity and Unreal",
        """The democratization of game development is largely due to the accessibility of powerful game engines like Unity and Unreal Engine. These platforms provide the core architecture-physics, rendering, and sound-allowing developers to focus on the creative aspects of their projects. For a software engineering student, understanding these engines is crucial, as they are increasingly used in industries beyond gaming, such as architecture and film production (e.g., The Mandalorian). The nuance of choosing an engine lies in the balance between performance and ease of use; while Unity is often preferred for mobile and 2D games, Unreal is the industry standard for high-fidelity, AAA graphics. In my opinion, the rise of these tools has lowered the barrier to entry, allowing diverse voices to share their stories in a medium that was once reserved for large corporations with proprietary technology.""",
    ),
    (
        "The Rise of Live Service Games",
        """The industry has shifted away from the one-time purchase model toward Games as a Service (GaaS). These titles, such as Fortnite or Destiny 2, are designed to be played for years, with constant updates, seasonal events, and new content. The advantage of this model is that it provides a stable revenue stream for developers and keeps the community active. However, it also creates a sense of fear of missing out (FOMO) among players, who feel pressured to play daily to unlock limited-time rewards. Consequently, many gamers complain about live service fatigue, where they feel overwhelmed by the number of games demanding their constant attention. In my view, while the model is commercially successful, it risks devaluing the finished artistic experience. Not every game needs to be an infinite platform; sometimes, a story is better when it has a clear beginning and end.""",
    ),
    (
        "The Impact of Cloud Gaming on Hardware Accessibility",
        """Cloud gaming services, such as Xbox Cloud Gaming or NVIDIA GeForce Now, allow players to stream high-end games to low-power devices like old laptops or smartphones. By moving the heavy processing to remote servers, the need for expensive consoles or gaming PCs is theoretically eliminated. Consequently, this could democratize gaming in regions where high-end hardware is unaffordable. The nuance of the problem, however, is the latency bottleneck; cloud gaming requires an extremely fast and stable internet connection to feel responsive. In my opinion, while the technology is impressive, we are still years away from it replacing local hardware entirely. If global internet infrastructure does not improve, cloud gaming will remain a luxury for those in well-connected urban areas, rather than a universal solution for the digital divide.""",
    ),
    (
        "Games as a Tool for Social and Political Commentary",
        """While often viewed as escapism, video games are increasingly being used as a medium for serious social and political commentary. Games like Papers, Please or This War of Mine force players to make difficult moral choices in oppressive systems, fostering empathy and understanding for real-world issues. Unlike a book or a movie, the interactive nature of a game makes the player complicit in the outcome, which deepens the emotional resonance. Consequently, these serious games are being used in classrooms and museums to discuss complex topics like immigration, war, and poverty. In my view, this is the ultimate proof of the medium's maturity. If a game can change how a person thinks about the world, it has achieved the highest purpose of art. As developers continue to experiment with these themes, games will play an even larger role in our cultural and political discourse.""",
    ),
]


STORY_TEXTS["c1"] = [
    (
        "The Ontology of the Avatar: The Duality of the Digital Self",
        """In the realm of immersive gaming, the avatar functions as more than a mere graphical representation; it is a sophisticated ontological bridge between the player's physical reality and the digital construct. The nuance of this relationship lies in the displacement of agency. When a player inhabits a character, they experience a form of dual consciousness, where the self is simultaneously the one pressing the buttons and the one navigating the dragon's lair. This phenomenon, often termed ludic embodiment, suggests that our sense of identity is more fluid and modular than traditional psychology would suggest. Consequently, the virtual world becomes a laboratory for exploring the what if of our own existence. Were it not for this capacity to project our consciousness into the machine, the emotional impact of interactive narrative would be significantly diminished. To understand the avatar is to recognize that in the 21st century, the self is no longer confined to the biological shell, but is distributed across a network of digital experiences.""",
    ),
    (
        "The Ethics of Procedural Rhetoric: Games as Persuasive Systems",
        """Ian Bogost coined the term procedural rhetoric to describe how games make arguments not through words or images, but through processes and rules. Unlike a book, which presents a static argument, a game forces the player to internalize a system's logic to succeed. The nuance of this persuasive power is most evident in serious games designed to simulate complex socio-political crises. By forcing the player to operate within the constraints of a specific system-such as the bureaucracy of a border crossing or the management of a failing economy-the game demonstrates the systemic nature of human problems. Consequently, the player's empathy is not generated through passive observation but through active complicity. This suggests that games are the most potent medium for political education, as they allow us to feel the invisible structures that govern our lives. To play a game is to engage with a theory of how the world works, and to master it is to understand the flaws within that theory.""",
    ),
    (
        "The Architecture of Choice: Determinism vs. Agency",
        """A central tension in modern game design is the conflict between the author's narrative intent and the player's desire for absolute agency. Designers often utilize the illusion of choice to provide a sense of freedom while maintaining a coherent story. The nuance of this architecture lies in the branching narrative, where the player is presented with critical moral dilemmas that appear to alter the game's outcome. However, a cynical analysis reveals that many of these choices are cosmetic, leading to the same conclusion regardless of the path taken. This ludic determinism raises profound questions about the nature of free will in a programmed environment. Consequently, some developers have experimented with emergent gameplay, where the system's rules allow for unpredictable outcomes that the designers never intended. This shift suggests that the future of interactive art is not about telling a story to a player, but about creating a space where the player can author their own meaning through the friction between their will and the code.""",
    ),
    (
        "The Semiotics of Space: Environmental Storytelling as Narrative Authority",
        """In the absence of traditional cinematic cutscenes, many modern games rely on environmental storytelling to convey their narrative depth. This technique transforms the physical layout of the game world into a semiotic landscape, where every object-a discarded toy, a bloodstain on the floor, an abandoned letter-serves as a piece of a larger historical puzzle. The nuance of this approach is that it rewards the observant player, turning the act of navigation into an act of investigation. Consequently, the narrative is not forced upon the audience; it is discovered at the player's own pace. This non-linear method of storytelling mirrors the way we perceive history in the real world-as a series of fragmented remains that must be reconstructed by the mind. This suggests that the most effective game worlds are those that function as palimpsests, where layers of past events are visible beneath the surface of the current gameplay, inviting the player to become a historian of the digital void.""",
    ),
    (
        "The Magic Circle and the Suspension of Social Reality",
        """The historian Johan Huizinga proposed the concept of the Magic Circle to describe the sacred space where the rules of the real world are suspended in favor of the rules of the game. Within this circle, an action that would be meaningless or even illegal in reality-such as hoarding digital gold or killing an opponent-becomes a source of intense meaning and prestige. The nuance of the Magic Circle lies in its fragility; it requires the absolute consent of all participants to function. Consequently, when a cheater breaks the rules, they do not just ruin the match; they shatter the ontological boundary that separates the game from the mundane. This suggests that gaming is a sophisticated form of social contract, a voluntary agreement to inhabit a fictional logic for the sake of play. As games increasingly integrate into our daily lives through augmented reality, the boundaries of the Magic Circle are becoming porous, challenging our traditional distinctions between seriousness and play.""",
    ),
    (
        "The Aesthetics of the Glitch and the Sublime of System Failure",
        """While the majority of game development is dedicated to the elimination of errors, a growing community of artists and speedrunners views the glitch as a site of sublime aesthetic and technical discovery. A glitch represents a moment where the system's logic fails, exposing the raw, underlying code that constitutes the digital world. The nuance of this experience is the breaking of the fourth wall from within the machine itself; the player is no longer a character in a story, but a witness to the limitations of the software. Consequently, glitch art has emerged as a genre that celebrates the beauty of distortion and the unpredictable nature of complex systems. This suggests that the perfect simulation is less interesting than the one that falters, as it is in the moment of failure that the ghost in the machine becomes visible. To master a glitch is to achieve a level of intimacy with the software that goes beyond the intended user experience, reaching into the very heart of the algorithmic process.""",
    ),
    (
        "The Political Economy of the Metaverse and Digital Labor",
        """The concept of the Metaverse-a persistent, interconnected virtual universe-is often marketed as a utopian escape. However, a critical C1 analysis reveals it to be a new frontier for platform capitalism and digital labor. Within these worlds, users are not just players; they are the primary producers of the content and data that give the platform its value. The nuance of this economy lies in the blurring of leisure and labor; by creating digital assets or participating in virtual social events, users are effectively working for the corporation that owns the server. Consequently, the freedom of the Metaverse is contingent upon the user's willingness to be monetized. This suggests that the future of digital space is a battleground for the sovereignty of the individual against the extractive logic of the network. To inhabit a virtual world is to navigate a complex legal and economic structure where your every movement is tracked, analyzed, and converted into corporate equity.""",
    ),
    (
        "The Ludo-Narrative Paradox of the Open World",
        """The open world genre promises the player total freedom, yet this freedom often creates a profound ludo-narrative dissonance. If the main story claims that the world is in immediate danger, but the player spends fifty hours collecting rare flowers or playing mini-games, the narrative urgency is entirely lost. The nuance of this paradox is the dilution of stakes; by providing too much choice, the designer risks stripping the main events of their emotional weight. Consequently, the player's experience becomes fragmented and unfocused. To solve this, some developers have turned to emergent narrative, where the world's systems generate their own stories based on the player's actions, rather than relying on a pre-written script. This suggests that the future of the open world is not in more content, but in more reactivity. A world that remembers what you did is far more immersive than one that merely offers a list of repetitive tasks.""",
    ),
    (
        "The Psychology of the Gacha and the Engineering of Desire",
        """The Gacha mechanic-a system where players spend currency for a random chance to win a virtual item-is a sophisticated application of variable ratio reinforcement. By utilizing the same psychological principles found in gambling, these games create a cycle of anticipation and reward that can be highly addictive. The nuance of this design is the normalization of the transaction; the game is built to feel like a hobby, while its underlying architecture is that of a casino. Consequently, the player's desire for a specific character or item is carefully engineered through limited-time events and power creep. This suggests that in the mobile market, the game is often a secondary layer designed to facilitate a continuous flow of microtransactions. To engage with a Gacha game is to enter a psychological battlefield where the designer's goal is to maximize lifetime value rather than provide a finished artistic experience.""",
    ),
    (
        "The Post-Human Future of AI-Generated Narratives",
        """As large language models become more sophisticated, we are entering an era where game narratives and dialogues can be generated in real-time by AI. This represents a radical shift from the static script to the infinite conversation, where every NPC can have a unique and unscripted interaction with the player. The nuance of this evolution is the loss of authorial control; if the story is generated by a machine, who is the creator? Furthermore, can an AI-authored story possess the emotional truth and thematic resonance that come from human experience? Consequently, we must reconsider our definition of creativity in the age of generative agents. This suggests that the role of the game designer will shift from writing stories to designing the parameters of stories-creating the world and the rules, but allowing the AI and the player to co-author the specific events. The game of the future will be a living, breathing entity that evolves with every interaction.""",
    ),
]


STORY_TEXTS["c2"] = [
    (
        "The Phenomenology of Presence: The Subjective Architecture of the Virtual",
        """The experience of presence within a digital environment-the psychological sensation of being there despite the physical body's stasis-represents a radical shift in our understanding of spatiality and consciousness. This is not merely a technical achievement of high-fidelity rendering, but a sophisticated negotiation between the player's cognitive faculty and the game's internal logic. To inhabit a virtual space is to engage in a tele-presence, where the self is projected across a technological void to inhabit a modular shell. The nuance of this state lies in the transparency of the interface; when the controller becomes an extension of the nervous system, the boundary between the real and the simulated dissolves. Consequently, the virtual world is no longer an object to be observed, but a reality to be lived. This suggests that consciousness is not inherently tied to the biological substrate, but can be redistributed across any system capable of providing a coherent sensory feedback loop. In the digital age, place is a function of attention rather than geography.""",
    ),
    (
        "The Metaphysics of the Rule: On the Sacred Geometry of Play",
        """Every game is a self-contained universe governed by a sacred geometry of rules-a set of ontological constraints that define the limits of the possible. Unlike the laws of physics, which are discovered, the rules of a game are willed into existence, creating a space where meaning is derived from the voluntary submission to arbitrary limitations. The nuance of this metaphysics is the teleology of the goal; because the game defines what victory looks like, it provides a sense of purpose and order that is often absent in the entropic reality of the mundane. Consequently, to play is to participate in a miniature cosmogony, a re-enactment of the act of creation through the establishment of logic. The beauty of the game lies in its finite perfection-a world where every action has a clear consequence and every problem has a potential solution. In this sense, gaming is a form of secular theology, a quest for a just world within the safe confines of the algorithmic circle.""",
    ),
    (
        "The Alchemical Transmutation of Failure: Perseverance as a Ludic Virtue",
        """In the traditional narrative arts, failure is a tragic conclusion; in gaming, however, failure is the materia prima of progress. This alchemical transmutation of the error turns the Game Over screen into a site of profound epistemological discovery. Each death or defeat serves to refine the player's understanding of the system's hidden mechanics, transforming raw frustration into strategic wisdom. The nuance of this process is the cultivation of the stoic self; the player must learn to view their own mistakes with a cold, analytical detachment. Consequently, the game becomes a crucible for the development of character, where persistence is rewarded more than innate talent. This suggests that the true value of the interactive medium is its capacity to teach us the art of the second chance-the realization that in the realm of the digital, as in life, the only terminal failure is the refusal to begin again. To master a difficult game is to achieve a victory over one's own entropic impulses.""",
    ),
    (
        "The Semiotics of the Hidden Level: On the Poetics of the Secret",
        """The hidden level or secret room functions as a powerful metaphor for the occult depths of the digital world. It is a space that exists outside the intended narrative trajectory, a reward for the player who refuses to be satisfied with the surface of the simulation. The nuance of the secret is its intentional invisibility; it is a dialogue between the designer and the most dedicated segment of the audience, a testament to the fact that the world is always larger than it appears. Consequently, the discovery of a secret triggers a sense of ontological vertigo-the realization that the reality we inhabit is layered with hidden histories and forgotten mechanics. This mirrors our own relationship with the physical universe, where every scientific discovery reveals a new level of complexity beneath the visible. The hidden level is a poetic reminder that curiosity is the ultimate key to the simulation, and that the most profound truths are often found in the places we were never meant to look.""",
    ),
    (
        "The Epistemology of the Save State: On the Illusion of Temporal Control",
        """The capacity to save one's progress-to capture a specific moment in time and return to it at will-represents a radical departure from the unidirectional flow of biological time. The Save State provides the player with a form of temporal sovereignty, an illusion of control over the entropic nature of existence. The nuance of this technology is the erasure of the consequence; because we can always return to a previous state, the weight of our choices is significantly diminished. Consequently, the game world becomes a laboratory for moral experimentation, where we can explore the darkest paths without the burden of permanent regret. This suggests a shift in our collective psyche toward a modular understanding of life, where history is a draft to be edited rather than a record to be lived. To save a game is to attempt a minor rebellion against the absolute authority of the clock, a search for a permanence that our biological reality can never provide.""",
    ),
    (
        "The Aesthetics of the Speedrun: On the Deconstruction of the Intentional",
        """The speedrun-the act of completing a game in the shortest time possible by exploiting glitches and optimized movement-functions as a radical deconstruction of the designer's authorial intent. The speedrunner does not inhabit the story; they interrogate the code. The nuance of this practice is the transcendence of the narrative; the characters and plot are discarded in favor of the pure, kinetic geometry of the software. Consequently, the game is transformed into a mathematical landscape, where the player moves with a god-like precision that defies the intended laws of the world. This represents a form of technological sublime, where the human mind achieves a level of intimacy with the machine that is almost post-human. To watch a speedrun is to witness the liberation of the software from the constraints of the human imagination, revealing the raw, algorithmic heart that beats beneath the skin of the story.""",
    ),
    (
        "The Ludo-Grief Phenomenon: On the Mourning of the Virtual Other",
        """As games increasingly utilize advanced AI and sophisticated writing to create emotionally complex companions, a new form of ludo-grief has emerged-the genuine sorrow felt upon the death of a digital entity. Unlike the grief felt for a character in a book, ludo-grief is intensified by the player's complicity in the outcome. If your actions failed to protect your companion, the mourning is coupled with a profound sense of personal guilt. The nuance of this emotion is its ontological ambiguity; we know the character is just code, yet our limbic system treats the loss as a biological reality. Consequently, the digital world becomes a site of real emotional labor. This suggests that as our lives become more integrated with the virtual, our capacity for empathy is expanding to encompass the non-biological. To mourn an AI is to acknowledge that meaning is not a property of the object, but a product of the relationship we build with the Other, regardless of its substrate.""",
    ),
    (
        "The Paradox of the Infinite Game: On the Stagnation of the Endless",
        """The rise of live service and procedurally generated infinite games promised a world where the adventure never ends. However, from a C2 perspective, this infinity often leads to a profound existential stagnation. Without the possibility of a conclusion, the actions within the game lose their narrative weight; if there is no end, there is no meaningful beginning. The nuance of this paradox is the erosion of the climax; the player is trapped in a state of perpetual middleness, a cycle of repetitive tasks that serves only to maintain the status quo of the simulation. Consequently, the infinite game becomes a metaphor for the treadmill of late-stage capitalism, where activity is divorced from purpose. This suggests that the most profound ludic experiences require the authority of the end-the realization that our time in the world is finite, and thus, every choice we make is a precious act of definition. A game that never ends is a game that never truly matters.""",
    ),
    (
        "The Architecture of the Loading Screen: On the Liminality of the Machine",
        """The loading screen, that brief interval where the hardware struggles to manifest the next segment of the digital world, serves as a vital liminal space between two realities. It is the moment where the suspension of disbelief is most vulnerable, as the player is forced to confront the mechanical reality of the disc spinning or the processor humming. The nuance of this interval is its temporal pause-a state of non-being where the player is neither in the old world nor the new. Consequently, the loading screen functions as a technological memento mori, a reminder that the digital paradise is a fragile construct that requires a constant influx of energy and data to survive. To wait for a game to load is to participate in the patience of the machine, a silent acknowledgment of the vast computational labor required to sustain our contemporary fantasies. The loading screen is the breathing room of the simulation.""",
    ),
    (
        "The Post-Human Gamer: On the Fusion of Neural and Digital Architectures",
        """As we look toward a future of direct neural interfaces and BCI (Brain-Computer Interface) gaming, the role of the gamer is evolving into a post-human synthesis of biological and digital architectures. The nuance of this evolution is the abolition of the controller; when the thought becomes the action, the delay between the will and the world vanishes. Consequently, the distinction between the internal thought and the external simulation will become increasingly difficult to maintain. This suggests a future where the game is not something we play, but something we become-a shared, hallucinatory reality where the boundaries of the self are as fluid as the code that supports them. This represents the ultimate ludic epiphany, a state where the human mind achieves a total, unmediated integration with the infinite possibilities of the virtual. To be a post-human gamer is to realize that the simulation is not a place we visit, but the final destination of our own evolutionary trajectory.""",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, equipamentos, acao e estruturas de preferencia",
    "a1": "presente simples, futuro com going to, generos de jogos, rotina e frequencia",
    "a2": "passado simples e continuo, comparativos, superlativos, hardware e nostalgia",
    "b1": "opiniao, argumentacao, impacto social e vocabulario tecnico comunitario",
    "b2": "game design, economia, narrativa interativa e vocabulario tecnico-analitico",
    "c1": "teoria ludica, ontologia digital e critica sistemica",
    "c2": "registro erudito, ensaio filosofico-ludico e densidade metafisica",
}


class Command(BaseCommand):
    help = "Replace the Games catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="games")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = STORY_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-games-{index:02d}-{title}")
                text.title = title
                text.summary_pt = self.summary_for(level, title, content)
                text.content_en = content
                text.level = level
                text.category = category
                text.character = None
                text.cover_image = ""
                text.word_count = words
                text.estimated_reading_time = max(1, round(words / 170))
                text.image_prompt = self.prompt_for(level, category, title, content)
                text.image_canvas_width = 500
                text.image_canvas_height = 500
                text.status = "published"
                text.published_at = text.published_at or timezone.now()

                if not options["dry_run"]:
                    text.save()
                    if not options["skip_assets"]:
                        animation_path = write_text_illustration(text)
                        if text.animation_asset.name != animation_path:
                            text.animation_asset = animation_path
                            text.save(update_fields=["animation_asset"])
                    if not options["skip_vocabulary"]:
                        replace_text_vocabulary(text, max_items=8)

                total += 1

            extra_texts = existing[len(entries):]
            if extra_texts and not options["dry_run"]:
                Text.objects.filter(id__in=[text.id for text in extra_texts]).delete()

        if range_warnings:
            self.stdout.write(self.style.WARNING("Word-count warnings:"))
            for warning in range_warnings:
                self.stdout.write(self.style.WARNING(warning))

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Games texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre games: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D educational video game magazine style, clean lines, high quality, "
            f"scene about {title}, showing {scene}, featuring the book-mascot Alexandrinho, "
            "using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
