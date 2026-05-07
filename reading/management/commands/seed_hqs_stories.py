import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Character, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


CHARACTERS = [
    ("Black Panther", "black-panther", "marvel"),
    ("Captain America", "captain-america", "marvel"),
    ("Captain Marvel", "captain-marvel", "marvel"),
    ("Deadpool", "deadpool", "marvel"),
    ("Doctor Strange", "doctor-strange", "marvel"),
    ("Hulk", "hulk", "marvel"),
    ("Iron Man", "iron-man", "marvel"),
    ("Spider-Man", "spider-man", "marvel"),
    ("Thor", "thor", "marvel"),
    ("Wolverine", "wolverine", "marvel"),
]


STORY_TEXTS = {}


STORY_TEXTS["iniciante"] = [
    (
        "Black Panther",
        "black-panther",
        """This is Black Panther. He is a king from Wakanda. His suit is black and silver. It is very strong. Black Panther is fast and brave. He protects his people and his country. He uses his claws to fight. He is a great hero.""",
    ),
    (
        "Captain America",
        "captain-america",
        """This is Captain America. He is a very old soldier, but he looks young. His suit is red, white, and blue. He has a round shield. The shield is indestructible. Captain America is a leader. He is very honest and strong.""",
    ),
    (
        "Captain Marvel",
        "captain-marvel",
        """This is Captain Marvel. She is a powerful pilot from Earth. Her suit is blue, red, and gold. She can fly in space. She has energy in her hands. Captain Marvel is very fast. She helps people on many different planets.""",
    ),
    (
        "Deadpool",
        "deadpool",
        """This is Deadpool. He is a funny character. His suit is red and black. He has two swords on his back. Deadpool can heal very fast. He talks a lot and tells many jokes. He is not a traditional hero, but he is cool.""",
    ),
    (
        "Doctor Strange",
        "doctor-strange",
        """This is Doctor Strange. He is a powerful sorcerer. He wears a blue suit and a red cloak. The cloak can fly. Doctor Strange uses magic to protect the world. He has a special necklace called the Eye of Agamotto. Magic is real for him.""",
    ),
    (
        "Hulk",
        "hulk",
        """This is Hulk. He is a very big and green monster. Usually, he is a scientist named Bruce Banner. When he is angry, he becomes Hulk. Hulk is the strongest character. He can jump very high and smash things. He is a hero with a big heart.""",
    ),
    (
        "Iron Man",
        "iron-man",
        """This is Iron Man. He is a genius billionaire. His real name is Tony Stark. He has a high-tech suit of armor. The suit is red and gold. Iron Man can fly and shoot lasers. He uses technology to save the world. He is very smart.""",
    ),
    (
        "Spider-Man",
        "spider-man",
        """This is Spider-Man. He is a young student from New York. His name is Peter Parker. He wears a red and blue suit. He can climb walls and shoot webs. Spider-Man is very fast and agile. He helps people in his neighborhood every day.""",
    ),
    (
        "Thor",
        "thor",
        """This is Thor. He is the God of Thunder. He is from a place called Asgard. He has a magic hammer called Mjolnir. Thor can control the lightning and the rain. He is very strong and he has long hair. He is a brave warrior.""",
    ),
    (
        "Wolverine",
        "wolverine",
        """This is Wolverine. He is a tough mutant. He has sharp claws in his hands. The claws are made of a metal called Adamantium. Wolverine can heal his body very fast. He is often serious and lonely. He is a member of the X-Men.""",
    ),
]


STORY_TEXTS["a1"] = [
    (
        "Black Panther (A1)",
        "black-panther",
        """T'Challa is the King of Wakanda, but he is also a superhero. Today, he is protecting his country from dangerous explorers. He is using his advanced technology to hide the city of Wakanda. His sister, Shuri, is helping him in the laboratory. She is very intelligent and she creates new gadgets for his suit. T'Challa is fighting because he wants to keep his people safe. He is a noble king and a loyal friend.""",
    ),
    (
        "Captain America (A1)",
        "captain-america",
        """Steve Rogers is Captain America. He is always training to be ready for battle. Right now, he is talking to the Avengers about a new mission. He is wearing his iconic shield on his arm. His best friend, Bucky, is often fighting by his side. They are working together to stop a villain named Red Skull. Steve is a hero because he believes in justice and freedom for everyone.""",
    ),
    (
        "Captain Marvel (A1)",
        "captain-marvel",
        """Carol Danvers is Captain Marvel, and she is incredibly strong. At this moment, she is flying through a distant galaxy. She is looking for people who need help in space. She is often working with Nick Fury from S.H.I.E.L.D. He is her mentor and friend. Carol is fighting against the Skrulls, but she is also trying to remember her past. She is a brave pilot with a powerful destiny.""",
    ),
    (
        "Deadpool (A1)",
        "deadpool",
        """Wade Wilson is Deadpool, and he is a very unusual hero. Currently, he is eating a taco and cleaning his swords. He is talking to the readers because he knows he is in a comic book! He is often working with his friend Weasel. Deadpool is looking for a villain named Ajax because he wants revenge. He is not a perfect person, but he is always having a lot of fun during his adventures.""",
    ),
    (
        "Doctor Strange (A1)",
        "doctor-strange",
        """Stephen Strange is the Sorcerer Supreme. Right now, he is meditating in his house, the Sanctum Sanctorum. He is protecting our dimension from dark magic. His friend Wong is studying ancient books with him. They are preparing for a battle against Dormammu. Stephen is a doctor, so he wants to heal the world in a different way. He is using his magical rings to create portals to other places.""",
    ),
    (
        "Hulk (A1)",
        "hulk",
        """Bruce Banner is a scientist, but he is struggling with his anger. When he is stressed, he becomes the Hulk. Currently, the Hulk is jumping over mountains and smashing tanks. He is very strong, so he is saving a group of people from a monster. His friend Betty Ross is trying to calm him down. Bruce is looking for a cure because he wants to be a normal man again. Hulk is powerful, but Bruce is very sad.""",
    ),
    (
        "Iron Man (A1)",
        "iron-man",
        """Tony Stark is Iron Man. Today, he is working on a new version of his armor. He is talking to his AI assistant, Jarvis. Tony is a billionaire, but he is using his money to help the world. His friend Pepper Potts is managing his big company, Stark Industries. They are working to stop a villain named Iron Monger. Tony is learning that being a hero is more important than being famous.""",
    ),
    (
        "Spider-Man (A1)",
        "spider-man",
        """Peter Parker is Spider-Man. This afternoon, he is swinging between the buildings of New York. He is looking for a thief in the streets. His Aunt May is waiting for him at home for dinner. Peter is a student, so he is also studying for a science test. He is fighting the Green Goblin because he wants to protect his city. Peter knows that with great power comes great responsibility.""",
    ),
    (
        "Thor (A1)",
        "thor",
        """Thor is the son of Odin. Right now, he is visiting Earth to help the Avengers. He is calling the lightning with his hammer. His brother, Loki, is often creating problems and playing tricks. Thor is trying to teach Loki how to be good. Thor is a god, but he is learning about human emotions. He is a powerful warrior who loves his friends and his family in Asgard.""",
    ),
    (
        "Wolverine (A1)",
        "wolverine",
        """Logan is Wolverine. At this moment, he is riding his motorcycle and looking for his past. He is a member of the X-Men, a group of mutants. He is working with Professor X to create a better world for everyone. Logan is fighting against Sabretooth, his old enemy. He is a tough man, but he is always protecting young mutants like Rogue. He is a hero with a mysterious history.""",
    ),
]


STORY_TEXTS["a2"] = [
    (
        "Black Panther (A2)",
        "black-panther",
        """T'Challa became the Black Panther after his father, King T'Chaka, died in a tragic attack. Before he became king, T'Challa studied in the best universities in Europe and America. He was more academic than other warriors. When he returned to Wakanda, he passed many difficult tests to prove his strength. He ate a special heart-shaped herb to gain his powers. This herb made him faster and stronger than a normal human. In the past, Wakanda was a secret place, but T'Challa decided to share its technology with the world. He realized that a king must be a leader for everyone, not just his own people.""",
    ),
    (
        "Captain America (A2)",
        "captain-america",
        """During World War II, Steve Rogers was a very thin and weak young man. He wanted to be a soldier, but the army rejected him many times. However, a scientist saw his brave heart and chose him for a secret experiment. Steve took a Super Soldier Serum, and suddenly he was taller and more muscular than anyone else. He became Captain America and fought against the Nazis. While he was finishing a dangerous mission, he fell into the icy ocean and stayed frozen for seventy years. When he woke up, the world was much more modern and faster than in the 1940s. It was a very difficult change for him.""",
    ),
    (
        "Captain Marvel (A2)",
        "captain-marvel",
        """Carol Danvers was a brave pilot in the United States Air Force. One day, while she was flying a secret plane, she had a terrible accident with an alien machine. The explosion changed her DNA and gave her cosmic powers. Before the accident, she was just a human, but after it, she became more powerful than a star! She lost her memory for a long time and lived with the Kree aliens. Later, she returned to Earth and remembered her real life. She discovered that she was stronger than she imagined. Now, she protects the galaxy and helps the Avengers when the situation is extremely dangerous.""",
    ),
    (
        "Deadpool (A2)",
        "deadpool",
        """Wade Wilson worked as a mercenary for many years. He was a funny man, but his life was very hard. When he discovered he had a serious disease, he accepted a dangerous offer to get a cure. The experiment was more painful than he expected! It gave him a powerful healing factor, but it also changed his face and his skin. He became Deadpool and decided to look for the men who hurt him. In the past, he was a regular soldier, but now he is an indestructible and crazy anti-hero. He is noisier and more violent than other heroes, but he sometimes does the right thing.""",
    ),
    (
        "Doctor Strange (A2)",
        "doctor-strange",
        """Stephen Strange was the most famous and arrogant neurosurgeon in New York. He was very rich, and he thought he was better than other doctors. However, a car accident destroyed the nerves in his hands. He couldn't perform surgery anymore. He spent all his money looking for a cure, but nothing worked. Finally, he traveled to the mountains in Nepal and met the Ancient One. He started to study magic and discovered that the mind is more powerful than a scalpel. He stopped being a selfish doctor and became the Sorcerer Supreme. His life now is much more mysterious and spiritual than his old life.""",
    ),
    (
        "Hulk (A2)",
        "hulk",
        """Dr. Bruce Banner was a brilliant scientist who worked with gamma radiation. During a test, he ran to save a teenager who was in the middle of the explosion. The gamma rays hit Bruce's body, but he didn't die. Instead, he transformed into a giant green monster. At first, he only transformed at night, but later, he changed every time he felt angry or stressed. The Hulk was much stronger and more aggressive than Bruce. For many years, the army hunted him because they were afraid of his power. Bruce felt more lonely than ever because he couldn't control the monster inside his soul.""",
    ),
    (
        "Iron Man (A2)",
        "iron-man",
        """Tony Stark was a billionaire who sold weapons to many countries. He didn't care about the consequences of his business. However, during a trip to a war zone, some enemies captured him. They forced him to build a missile, but Tony had a better idea. With the help of another prisoner, he built a suit of armor to escape. This first suit was larger and heavier than his modern armors. When he returned home, he realized that his weapons were dangerous. He stopped selling them and decided to use his technology to protect people. He became Iron Man and transformed his life from a selfish businessman to a selfless hero.""",
    ),
    (
        "Spider-Man (A2)",
        "spider-man",
        """Peter Parker was a shy and nerdy student who lived with his Uncle Ben and Aunt May. During a school trip to a laboratory, a radioactive spider bit his hand. The next day, he discovered he was stronger and faster than any athlete in his school. He could also climb walls! At first, he used his powers to win money in wrestling matches. But one night, he didn't stop a thief, and that same thief killed his Uncle Ben. Peter was very sad and guilty. He realized that with great power comes great responsibility. He became Spider-Man to protect New York and stop criminals.""",
    ),
    (
        "Thor (A2)",
        "thor",
        """Thor was always a powerful warrior, but in the past, he was very arrogant and proud. He thought he was the most important god in Asgard. Because of his bad behavior, his father, Odin, took his powers away and sent him to Earth. Thor lived as a normal human for a while and learned how to be humble. He met Jane Foster and realized that humans are brave and kind. When he was ready to sacrifice his life to save others, his magic hammer, Mjolnir, returned to his hand. He became the God of Thunder again, but he was a much wiser and better man than before.""",
    ),
    (
        "Wolverine (A2)",
        "wolverine",
        """Logan lived for more than a hundred years because his body heals very fast. In the past, a secret government organization called Weapon X kidnapped him. They wanted to create the perfect soldier. They performed a terrible surgery and covered his bones with a metal called Adamantium. This made his claws indestructible and stronger than any weapon. The experiment was the most painful experience of his long life. He lost his memory and lived like an animal in the forest for a long time. Later, Professor X found him and invited him to join the X-Men. Logan found a new family, but he still carries the scars of his dark past.""",
    ),
]


STORY_TEXTS["b1"] = [
    (
        "Black Panther (B1)",
        "black-panther",
        """T'Challa faces a constant dilemma between his duty as a King and his role as a superhero. In the past, Wakanda was kept hidden to protect its resources, but T'Challa believes that its technology should be used to help the entire world. However, this decision has consequences. By opening the borders, Wakanda might be exposed to international conflicts and greed. Consequently, T'Challa must be more careful than ever to protect his culture while being a global leader. He is often criticized by those who prefer isolation. In my opinion, his leadership is essential because he proves that power must be combined with compassion. Therefore, being the Black Panther is not just about fighting; it is about navigating the complex politics of a modern world while staying true to his ancestors.""",
    ),
    (
        "Captain America (B1)",
        "captain-america",
        """For Steve Rogers, the greatest challenge is not the physical battle, but the feeling of being a man out of time. Because he was frozen for decades, the moral clarity of the 1940s has been replaced by a much more complex political landscape. He often wonders if the values he fought for still exist in today's society. Consequently, he sometimes finds himself in conflict with government organizations that prioritize security over freedom. In his view, justice should not be compromised for the sake of convenience. He must decide when to follow orders and when to follow his own conscience. Captain America represents the ideal of what a hero should be, but he also reminds us that standing up for what is right is often a lonely and difficult journey.""",
    ),
    (
        "Captain Marvel (B1)",
        "captain-marvel",
        """Carol Danvers possesses immense cosmic power, which means she is often responsible for the safety of entire star systems. Because she is one of the strongest beings in the universe, she must decide where her presence is most needed. This creates a sense of universal guilt when she cannot be everywhere at once. Furthermore, her human past and her Kree military training often clash, making her question her true identity. In my opinion, her struggle shows that even with god-like powers, a person can still feel uncertain about their place in the world. Consequently, she spends most of her time in deep space, protecting vulnerable civilizations from interstellar threats. She must balance her immense strength with the wisdom to know when to intervene and when to let a planet find its own path.""",
    ),
    (
        "Deadpool (B1)",
        "deadpool",
        """Deadpool is a unique case because he is fully aware that he is a fictional character in a comic book. This breaking of the fourth wall allows him to comment on the tropes and cliches of the superhero genre. While he is often seen as a joke, his life is actually quite tragic. Because he cannot die, he suffers from a constant cycle of pain and regeneration. Consequently, he uses humor as a defense mechanism to cope with his mental instability. He might not follow a traditional moral code, but he often helps those who are rejected by society. In my view, Deadpool represents the chaos of the modern world. He shows us that even in the most ridiculous situations, a person can find a reason to keep moving forward, even if that reason is just for a laugh.""",
    ),
    (
        "Doctor Strange (B1)",
        "doctor-strange",
        """As the Sorcerer Supreme, Stephen Strange is responsible for protecting our reality from mystical threats that most people cannot even imagine. Because magic is a dangerous and unpredictable force, every spell he casts has a potential price. He must be extremely disciplined to avoid being corrupted by the dark dimensions he monitors. Consequently, he often has to make cold, calculated decisions that others might find heartless. For instance, he might sacrifice a small thing to save the entire multiverse. In my opinion, his character highlights the weight of secret knowledge. He lives in a world of shadows and ancient rituals, ensuring that the sun rises every morning without the public ever knowing how close they came to destruction. He is the silent guardian of the impossible.""",
    ),
    (
        "Hulk (B1)",
        "hulk",
        """The tragedy of Bruce Banner is the lack of control over his own body and mind. Because the Hulk is fueled by rage, Bruce is constantly afraid of hurting the people he loves. Consequently, he has spent years living in isolation, trying to suppress the monster within. However, there are situations where the Hulk's strength is the only thing that can save the world. This creates a painful irony: the world needs the very thing that Bruce hates most about himself. He must learn to coexist with his other half rather than just trying to destroy it. In my view, the Hulk is a metaphor for the repressed emotions we all carry. He reminds us that our strength and our weaknesses are often two sides of the same coin, and that true power comes from understanding our darkest parts.""",
    ),
    (
        "Iron Man (B1)",
        "iron-man",
        """Tony Stark's journey is defined by the consequences of his own inventions. In the past, his weapons were used to cause suffering, and now he must spend his life trying to undo that damage. Because he is a futurist, he is always trying to create technology that can protect the planet from future threats. However, his hero complex sometimes leads him to make dangerous mistakes, such as creating AI that becomes uncontrollable. Consequently, he must learn that technology cannot solve every human problem. In my opinion, Tony represents the ambition and the ego of the modern age. He is a man who wants to build a suit of armor around the world, but he eventually realizes that the most important thing is the human heart inside the machine.""",
    ),
    (
        "Spider-Man (B1)",
        "spider-man",
        """Peter Parker's life is a constant struggle to balance his personal desires with his heroic responsibilities. Because he is a street-level hero, he sees the direct impact of crime on his community every day. Consequently, he often misses important events in his private life, like dates or exams, to stop a robbery or help a neighbor. This Spider-Man luck makes him one of the most relatable characters in comics. He must decide every day if the sacrifice is worth it. In my view, Peter proves that you don't need to be a billionaire or a god to be a hero; you just need to care about your community. Despite the constant stress and financial problems, he continues to fight because he knows that if he doesn't, no one else will.""",
    ),
    (
        "Thor (B1)",
        "thor",
        """Thor's main conflict is the balance between his divinity and his humanity. Because he is an immortal god, he has seen empires rise and fall, which can make him feel detached from the short lives of humans. However, his time on Earth has taught him the value of mortality and the courage of those who face death every day. He must prove himself worthy of Mjolnir not through strength, but through his character. Consequently, he often finds himself defending Earth against his own people from Asgard. In my opinion, Thor's story is about the burden of legacy. He must decide if he wants to be the King his father wants, or the hero that the world needs. He represents the nobility of service and the humility of a powerful being who chooses to protect the weak.""",
    ),
    (
        "Wolverine (B1)",
        "wolverine",
        """Logan is a man who has lived too long and seen too much violence. Because he has a dark past as a government weapon, he struggles with the feeling that he is more of an animal than a man. His primary dilemma is whether he can ever truly find peace or if he is destined to fight forever. Consequently, he often acts as a mentor to young mutants, trying to prevent them from making the same mistakes he did. In my view, Wolverine represents the lone wolf who eventually finds a pack. Despite his gruff exterior and violent methods, he has a deep sense of honor and loyalty to the X-Men. He shows us that even if you have been broken by life, you can still choose to be a protector and a friend.""",
    ),
]


STORY_TEXTS["b2"] = [
    (
        "Black Panther (B2)",
        "black-panther",
        """The Black Panther serves as a powerful deconstruction of the Third World trope, presenting Wakanda as a technologically superior isolationist state. The narrative often interrogates the tension between tradition and globalization. T'Challa, as a monarch, must navigate the ethical complexities of interventionism; by revealing Wakanda's secrets, he risks the commodification of his culture. Consequently, the stories often function as an allegory for the African diaspora and the reclaiming of stolen legacies. In my opinion, the character's significance lies in his dual identity as both a diplomat and a warrior, representing a sophisticated blend of political realism and superhero fantasy. He challenges the audience to consider how a nation's wealth should be utilized in a fractured global landscape.""",
    ),
    (
        "Captain America (B2)",
        "captain-america",
        """Captain America is frequently misinterpreted as a symbol of blind nationalism, whereas the character is actually intended to represent the American Dream in its most idealistic form. This distinction is crucial; Steve Rogers often finds himself in opposition to the government when its actions deviate from his core principles of liberty and justice. Consequently, he has become a personification of the moral compass in the Marvel Universe. The nuance of his character lies in his internal conflict regarding the loss of the perceived simplicity of the 1940s. In my view, he is a tragic figure who maintains his integrity in an era of moral ambiguity. His shield is not just a weapon, but a symbol of defense in a world that often prioritizes preemptive aggression.""",
    ),
    (
        "Captain Marvel (B2)",
        "captain-marvel",
        """Carol Danvers represents the evolution of the female superhero from a secondary character to a pillar of cosmic authority. Her narrative often centers on the theme of unsolicited power and the reclaiming of agency after years of manipulation by external forces. Because her abilities are so immense, she is often depicted as a detached figure, struggling to maintain a connection with her humanity. Consequently, her stories explore the psychological toll of being a universal deterrent. In my opinion, Captain Marvel is a vital archetype for modern empowerment, illustrating that strength is not merely about physical force, but about the autonomy to define one's own destiny. She serves as a bridge between Earth's grounded conflicts and the vast, alien complexities of the multiverse.""",
    ),
    (
        "Deadpool (B2)",
        "deadpool",
        """Deadpool is the ultimate postmodern hero, utilizing meta-commentary to deconstruct the very medium he inhabits. His awareness of the fourth wall allows him to acknowledge the absurdity of superhero tropes, providing a cynical yet hilarious critique of the industry. The nuance of Deadpool is the juxtaposition of his nihilistic humor with his profound physical and emotional suffering. Consequently, he serves as a reminder that the invincibility of superheroes is often a curse rather than a gift. In my view, he is a necessary subversion of the genre, proving that a character can be morally bankrupt and deeply flawed yet still possess a strange, infectious sense of humanity. He is the jester of the Marvel Universe, speaking truths that more serious heroes refuse to acknowledge.""",
    ),
    (
        "Doctor Strange (B2)",
        "doctor-strange",
        """Doctor Strange represents the intersection of science, mysticism, and the limits of human perception. His transition from a rationalist neurosurgeon to a master of the mystic arts is a classic ego-death narrative. Consequently, his adventures often involve abstract, non-linear threats that cannot be solved through physical strength alone. The nuance of the character is the burden of the unseen; Strange operates in dimensions that are invisible to the public, sacrificing his reputation and sanity to protect a world that doesn't even know it is in danger. In my opinion, he reflects the human desire to find meaning beyond the material plane. He is a guardian of the cosmic order, reminding us that there are forces in the universe that transcend our current scientific understanding.""",
    ),
    (
        "Hulk (B2)",
        "hulk",
        """The Hulk is perhaps the most enduring modern retelling of the Jekyll and Hyde myth, exploring the duality of man and the dangers of repressed trauma. Bruce Banner's anger is manifested as a physical entity that he cannot control, turning his internal struggle into a public catastrophe. Consequently, the Hulk is often viewed as a force of nature rather than a traditional hero. The nuance of the character lies in the shifting versions of the Hulk-from the mindless savage to the intelligent professor-reflecting Bruce's complex mental state. In my view, the Hulk is a profound metaphor for the destructive potential of the human psyche when it is pushed to its limits. He challenges the notion that power is something to be mastered, suggesting instead that it is something to be survived.""",
    ),
    (
        "Iron Man (B2)",
        "iron-man",
        """Tony Stark is the personification of the techno-optimism of the 21st century, yet his stories are often a cautionary tale about the arrogance of innovation. As a character defined by his intellect, his primary struggle is the God complex that comes with creating world-altering technology. Consequently, his greatest enemies are often his own creations or the legacy of his past mistakes. The nuance of Iron Man is the vulnerability of the man inside the suit; without his technology, Tony is a fragile human battling addiction and ego. In my opinion, he represents the ethical dilemmas of the modern military-industrial complex. He is a hero who is constantly trying to patch the world's problems with software and steel, often failing to realize that some problems are fundamentally human.""",
    ),
    (
        "Spider-Man (B2)",
        "spider-man",
        """Spider-Man remains the most relatable hero because his struggles are rooted in the mundane difficulties of everyday life. Unlike billionaires or gods, Peter Parker must worry about rent, relationships, and his reputation. Consequently, the Spider-Man mythos is built on the concept of the proletarian hero. The nuance of the character is the cost of heroism; every time Peter saves the city, his personal life suffers. In my view, he is the ultimate archetype of responsibility, illustrating that having power is not a privilege, but a heavy duty. He is the Everyman who chooses to be extraordinary, proving that the most heroic act is not defeating a supervillain, but continuing to do the right thing despite constant personal loss and exhaustion.""",
    ),
    (
        "Thor (B2)",
        "thor",
        """Thor's narrative arc is a study in divine humility and the burden of immortality. As a god who chooses to protect a mortal world, he is constantly forced to reconcile his eternal perspective with the fleeting nature of human life. Consequently, his stories often deal with themes of legacy, worthiness, and the twilight of the gods. The nuance of the character is the estrangement from his own kind; by choosing Earth (Midgard), Thor becomes an exile from Asgard. In my opinion, he represents the noble ideal of using immense power in the service of the vulnerable. He is a bridge between ancient mythology and modern heroism, illustrating that even a god must prove his worth through his actions rather than his birthright.""",
    ),
    (
        "Wolverine (B2)",
        "wolverine",
        """Wolverine is the quintessential anti-hero whose character is defined by the tension between his animalistic instincts and his desire for redemption. His longevity allows his stories to span decades of historical trauma, from world wars to secret experiments. Consequently, he is a character haunted by a past he cannot fully remember. The nuance of Wolverine is the paradox of the loner; while he claims to prefer isolation, he is a foundational member of the X-Men and a mentor to many. In my view, he represents the struggle to remain civilized in a violent world. He is a survivor who has been broken and rebuilt so many times that his very bones are a weapon, yet he maintains a fierce, hidden sense of nobility and love for his found family.""",
    ),
]


STORY_TEXTS["c1"] = [
    (
        "Black Panther (C1)",
        "black-panther",
        """The narrative of Black Panther serves as a sophisticated inquiry into the ethics of isolationism and the responsibilities of a technologically advanced state in a fractured global landscape. Historically represented as a reclusive kingdom, Wakanda under T'Challa's reign must grapple with the sovereign's dilemma: whether to maintain its strategic advantage or intervene in the systemic injustices that plague the African diaspora. This tension is often explored through the lens of post-colonial theory, where Wakanda represents an uncolonized imagination. Consequently, the Black Panther is not merely a vigilante but a head of state whose actions carry significant diplomatic weight. The nuance of the character lies in the delicate balance between preserving an ancient cultural heritage and embracing the inevitabilities of globalization. In my opinion, the stories function as a radical critique of traditional developmental narratives, proposing a world where African excellence is the primary driver of global technological progress.""",
    ),
    (
        "Captain America (C1)",
        "captain-america",
        """Captain America functions as a complex semiotic site where the ideals of American democracy are constantly interrogated and deconstructed. Unlike a blind instrument of the state, Steve Rogers represents the critical patriot-an individual whose loyalty is to the foundational principles of the Constitution rather than the transient interests of the government. Consequently, his narrative arc often involves a defiant opposition to institutional overreach and the erosion of civil liberties. The nuance of his character is the burden of the symbol; he must inhabit an icon that is frequently co-opted for propaganda, a struggle that often leaves him estranged from the very society he seeks to protect. In my view, he is a tragic figure of moral absolute in a world of ethical relativism, serving as a reminder that the true American Dream requires a constant, often subversive, defense against those who would exploit it for power.""",
    ),
    (
        "Captain Marvel (C1)",
        "captain-marvel",
        """Carol Danvers embodies the shift toward a cosmic feminism that challenges the historical marginalization of female agency within the superhero canon. Her character trajectory is defined by the reclamation of her narrative from military and alien institutions that sought to weaponize her power for their own ends. Consequently, the stories often function as an allegory for the breaking of the glass ceiling and the psychological cost of attaining institutional authority. The nuance of Captain Marvel lies in her position as a trans-galactic enforcer, where her strength is so absolute that it creates a profound sense of detachment from the human experience. In my opinion, she represents the dilemma of the modern superpower: the difficulty of exercising immense force without becoming an oppressive figure. She is a guardian of the marginalized on a universal scale, proving that true power lies in the autonomy to choose one's own mission.""",
    ),
    (
        "Deadpool (C1)",
        "deadpool",
        """Deadpool serves as the primary disruptor of the Marvel mythos, utilizing a radical form of meta-textual irony to expose the artificiality of the comic book medium. By consistently shattering the fourth wall, he refuses to participate in the serious moralizing that characterizes traditional hero narratives. The nuance of his character lies in the juxtaposition of his nihilistic levity with a body that is a site of perpetual trauma and regeneration. Consequently, he functions as a critique of the invincibility trope, suggesting that the superhero's life is an endless cycle of suffering sanitized for entertainment. In my view, Deadpool is a postmodern jester whose role is to speak truth to power by mocking the very genre that sustains him. He reminds the audience that the hero's journey is often a calculated corporate product, offering a messy, chaotic alternative to the polished narratives of his peers.""",
    ),
    (
        "Doctor Strange (C1)",
        "doctor-strange",
        """Doctor Strange represents the philosophical bridge between the rationalism of the Enlightenment and the occult depths of the metaphysical. His role as the Sorcerer Supreme is not merely one of combat, but of ontological maintenance-ensuring the stability of a reality that is constantly threatened by extradimensional entropy. Consequently, his narratives often engage with themes of epistemological humility, where the pursuit of absolute knowledge leads to the dissolution of the self. The nuance of the character is the ethics of the secret; he must operate in a shadow world of rituals and sacrifices that are, by necessity, hidden from the public. In my opinion, he reflects the human anxiety regarding the limits of science and the suspicion that our reality is merely a thin veneer over a vast, unknowable abyss. He is the institutional guardian of the impossible, protecting a society that remains blissfully unaware of its own fragility.""",
    ),
    (
        "Hulk (C1)",
        "hulk",
        """The Hulk serves as a potent critique of the military-industrial complex and the devastating consequences of scientific hubris. The character is a physical manifestation of the unintended consequence-a product of weapons research that has become a permanent, uncontrollable threat to the status quo. Consequently, the stories often explore the ethics of containment and the dehumanization of those who fall outside the norm of social stability. The nuance of the Hulk lies in the profound alienation of Bruce Banner, a man who is literally hunted by his own shadows. In my view, the character is a modern retelling of the Prometheus myth, illustrating the psychic fragmentation that occurs when human ambition is divorced from moral responsibility. He is a tragic reminder that the primal forces of nature, once unleashed, cannot be re-bottled by the institutions that sought to exploit them.""",
    ),
    (
        "Iron Man (C1)",
        "iron-man",
        """Tony Stark functions as a personification of platform capitalism and the neoliberal ideal of the techno-savior. His evolution from a munitions manufacturer to a global protector reflects the shift toward a society where private corporations increasingly fulfill the roles traditionally held by the state. The nuance of the character is the surveillance-security paradox; in his quest to protect the world, he frequently creates systems-such as advanced AI and global monitoring networks-that threaten the very privacy they are meant to secure. Consequently, his narrative often critiques the arrogance of the billionaire-philanthropist who believes that all social problems can be solved through engineering. In my opinion, Iron Man represents the fragility of the modern suit of armor, highlighting the ethical void that exists when innovation is prioritized over humanistic values.""",
    ),
    (
        "Spider-Man (C1)",
        "spider-man",
        """Spider-Man remains the most significant critique of the heroic elite, situating the struggle for justice within the precarious realities of the working class. Peter Parker's narrative is defined by the opportunity cost of altruism, where his commitment to the public good results in perpetual financial and social instability. Consequently, the stories interrogate the myth of the meritocracy; despite his genius and physical power, Peter remains a marginal figure, struggling to survive in an unforgiving urban economy. The nuance of the character is his refusal to succumb to cynicism despite the institutional neglect he faces. In my view, he is the ultimate proletarian hero, illustrating that true responsibility is not found in grand cosmic battles, but in the daily, unglamorous sacrifices made for one's community. He is the conscience of the street-level experience.""",
    ),
    (
        "Thor (C1)",
        "thor",
        """Thor represents the intersection of ancient mythological authority and the democratic requirements of the modern era. His character arc is a sustained meditation on the legitimacy of power-the question of what makes a ruler worthy in a world that no longer accepts the divine right of kings. Consequently, his exile to Midgard functions as a deconstruction of his own godhood, forcing him to earn his status through service rather than birthright. The nuance of the character lies in his cultural estrangement; he is a being of eternal cycles trapped in a world of linear progress and inevitable death. In my opinion, Thor reflects the modern struggle to maintain a sense of the sacred in a secular world. He is a bridge between the archaic past and the technological future, demonstrating that true nobility is a constant performance of humility and sacrifice.""",
    ),
    (
        "Wolverine (C1)",
        "wolverine",
        """Wolverine serves as a visceral site for exploring the trauma of institutional weaponization and the erasure of individual identity by the state. His history with the Weapon X program functions as a critique of cold-war ethics, where the human body is treated as a disposable resource for military advancement. Consequently, his narrative is one of reconstructive memory, as he struggles to reclaim a self that was systematically dismantled. The nuance of the character is the beast-man dialectic; he is a creature of primal violence who nevertheless strives for a civilized morality. In my view, Wolverine represents the survivor of systemic abuse who refuses to become the monster the system intended him to be. He is the lone wolf whose primary struggle is not against his enemies, but against the internal programming that would deny him his humanity.""",
    ),
]


STORY_TEXTS["c2"] = [
    (
        "Black Panther (C2): The Afrofuturist Sovereign and the Ontological Shield",
        "black-panther",
        """The figure of the Black Panther operates as a radical ontological pivot within the Western superhero canon, representing the apotheosis of an uncolonized African intellect. Wakanda is not merely a geographic location but a technological sublime-a space where the ancestral and the futuristic coexist in a seamless, non-linear progression. T'Challa, therefore, embodies the sovereign's paradox: he is the guardian of a tradition that is simultaneously the vanguard of global innovation. The nuance of this sovereignty lies in the Heart-Shaped Herb, a botanical conduit that bridges the biological self with the Ancestral Plane, suggesting that true power is a genealogical inheritance rather than an individual acquisition. Consequently, the Black Panther serves as a critique of the scarcity mindset of the global North, offering instead a vision of vibranium-based abundance that challenges the historical erasure of Black agency. To inhabit the cowl is to become a living palimpsest of a history that refuses to be suppressed, a monarch who rules not by divine right, but by the merit of a wisdom that spans millennia.""",
    ),
    (
        "Captain America (C2): The Anachronistic Ideal and the Semiotics of the Shield",
        "captain-america",
        """Steve Rogers represents the anachronistic ideal-a moral absolute cast into a world of liquid modernity and ethical relativism. He is the man out of time whose very existence serves as a silent, yet thunderous, indictment of contemporary institutional decay. The nuance of his character lies in the shield: a concave disc of vibranium-steel alloy that is physically indestructible yet symbolically fragile. It is an instrument of pure defense, embodying a refusal to strike first, which contrasts sharply with the preemptive aggression of the modern surveillance state. Consequently, Captain America is often a subversive figure, standing in opposition to the security-at-all-costs logic of the military-industrial complex. His struggle is the preservation of the spirit against the machinery of the state, proving that the true American Dream is a radical commitment to individual liberty that must, at times, become an act of rebellion against the very flag he wears. He is the ghost of a promised future that we have yet to earn.""",
    ),
    (
        "Captain Marvel (C2): The Cosmic Absolute and the Transcendence of the Binary",
        "captain-marvel",
        """Carol Danvers serves as a manifestation of the cosmic absolute, a character whose power scale necessitates a detachment from the terrestrial and a commitment to the interstellar equilibrium. Her narrative arc is a sophisticated deconstruction of gaslighting and institutional erasure, as she reclaims her memories and her agency from those who sought to reduce her to a mere weapon. The nuance of her godhood is the burden of the deterrent; she is a presence so formidable that her mere existence shifts the geopolitical (and galactopolitical) balance of power. Consequently, she inhabits a state of perpetual exile, belonging to neither Earth nor the Kree Empire, but to the vast, entropic void she protects. This suggests that the highest form of power requires a total dissolution of the local self in favor of a universal responsibility. Captain Marvel is the binary star of the Marvel mythos-a source of blinding light that reveals the smallness of our terrestrial conflicts against the infinite scale of the multiverse.""",
    ),
    (
        "Deadpool (C2): The Mercenary of the Meta-Text and the Nihilism of the Page",
        "deadpool",
        """Wade Wilson is the terminal symptom of postmodernity-a character who has pierced the veil of his own fictionality and found only a chaotic, laughing void. By consistently shattering the fourth wall, Deadpool performs a radical de-sacralization of the superhero mythos, exposing the strings of the corporate puppeteers who govern his reality. The nuance of his condition is the horror of the eternal; because he cannot die, his existence is a repetitive cycle of trauma sanitized for a voyeuristic audience. Consequently, his humor is not a distraction, but a visceral defense mechanism against the realization that he is a slave to the ink. This meta-textual awareness transforms him into a ludic nihilist who finds freedom in the absurdity of his own suffering. He is the jester at the edge of the world, proving that in a reality defined by artifice, the only authentic act is to mock the medium that grants you life.""",
    ),
    (
        "Doctor Strange (C2): The Architect of the Invisible and the Epistemology of the Void",
        "doctor-strange",
        """Stephen Strange represents the epistemological surrender-the moment where the analytical mind of the surgeon recognizes the absolute sovereignty of the irrational. His role as the Sorcerer Supreme is a form of ontological maintenance, a constant labor of keeping the fragmented dimensions of reality from collapsing into each other. The nuance of his magic is the ethics of the cost; unlike the clean utility of technology, magic in the Strange mythos is an extractive and dangerous force that leaves permanent scars on the soul of the practitioner. Consequently, he is a figure of profound intellectual loneliness, possessing a vision of the universe that is entirely incomprehensible to the society he preserves. He is the guardian of the hidden order, a bridge between the clinical rationalism of the hospital and the chaotic sublime of the Dark Dimension. To be Doctor Strange is to accept that the universe is a haunted house of infinite rooms, and that sanity is merely a thin, fragile light in a vast, encroaching shadow.""",
    ),
    (
        "Hulk (C2): The Gamma-Irradiated Shadow and the Phenomenology of Rage",
        "hulk",
        """The Hulk is the primal scream of the scientific age-a physical manifestation of the repressed trauma and unbridled id that lurks beneath the surface of civilized humanity. Bruce Banner's struggle is a phenomenological rupture, where the rational self is periodically usurped by a force of pure exteriority that refuses to be contained by social or physical laws. The nuance of the Green Goliath is the tragic innocence of the monster; the Hulk does not seek destruction, but stasis-the desire to be left alone in a world that insists on weaponizing him. Consequently, the Hulk functions as a critique of Promethean hubris, illustrating that the fire we steal from the gods will inevitably consume the thief. He is the gamma-irradiated shadow of Jungian psychology, a reminder that the more we suppress our capacity for violence, the more devastating its eventual eruption will be. The Hulk is the monstrous real that defies the symbolic order.""",
    ),
    (
        "Iron Man (C2): The Post-Human Suit and the Narcissism of Innovation",
        "iron-man",
        """Tony Stark represents the technological apotheosis of the individual-a man who has transcended his biological fragility by fusing his nervous system with an ever-evolving digital shell. He is the sovereign innovator who believes that the world's tragedies are merely bugs that can be patched with better software. The nuance of the Invincible Iron Man is the fragility of the core; the suit is a response to a literal and metaphorical hole in the heart, a desperate attempt to protect a vulnerable interiority with an impenetrable exteriority. Consequently, his narrative is one of cyclical hubris, where his attempts to build a suit of armor around the world inevitably result in the creation of new, more sophisticated threats. He is the narcissistic savior of the neoliberal era, a hero who struggles to realize that the most profound problems are not mechanical, but human-and that no amount of steel can shield a soul from the consequences of its own arrogance.""",
    ),
    (
        "Spider-Man (C2): The Ethics of the Proletarian Hero and the Gravity of Responsibility",
        "spider-man",
        """Spider-Man is the ultimate ethical anchor of the superhero genre, grounding the cosmic and the spectacular in the gritty, precarious reality of the Everyman. Peter Parker's existence is defined by the ludo-narrative dissonance of his life: he possesses the power of a god but is constantly defeated by the requirements of a landlord. The nuance of the Web-Slinger is the permanence of the sacrifice; every heroic act is a withdrawal from the bank of his personal happiness, leading to a life of perpetual exhaustion and financial instability. Consequently, he represents the proletarianization of heroism, proving that true responsibility is a heavy, unglamorous burden that offers no rest and little reward. He is the conscience of the neighborhood, a hero who remains friendly because he refuses to detach himself from the human struggle. Spider-Man proves that the most heroic act is not the salvation of the world, but the quiet, persistent refusal to give up on the person next to you.""",
    ),
    (
        "Thor (C2): The Divine Anachronism and the Twilight of Worthiness",
        "thor",
        """Thor serves as an inter-temporal bridge between the archaic cycles of myth and the linear progress of modernity. He is a being of eternal recurrence forced to inhabit a world characterized by planned obsolescence. The nuance of his godhood is the concept of worthiness-a moral imperative that transcends mere physical strength and requires a constant, active alignment with the virtues of humility and sacrifice. Consequently, Thor's hammer, Mjolnir, is not a weapon, but an ontological judge that assesses the soul of its wielder in real-time. This suggests that nobility is not an inherited status, but a precarious state of being that must be earned with every breath. He is the immortal witness to human finitude, a god who finds the sacred in the very mortality he lacks. To be Thor is to live in the shadow of Ragnarok, recognizing that while the gods may fall, the duty to protect is as eternal as the lightning.""",
    ),
    (
        "Wolverine (C2): The Archaeology of the Beast and the Sisyphus of Regeneration",
        "wolverine",
        """Logan is a living archive of violence, a character whose longevity and regenerative factor have turned his body into a site of historical trauma and geological time. He is the Wolverine-a creature of primal instinct who has been technologized into a weapon by the very civilization he protects. The nuance of his existence is the horror of memory; because he heals from every wound, his scars are not on his skin, but in his mind-a fragmented tapestry of wars, experiments, and losses. Consequently, he represents the Sisyphus of the battlefield, a man condemned to outlive everyone he loves while remaining a permanent target for those who would exploit his adamantium bones. His struggle is the cultivation of the human in the heart of the beast, a refusal to become the mindless predator the system intended him to be. Wolverine is the lone wolf who chooses the pack, proving that even a creature of pure iron and rage can find redemption in the protection of the innocent.""",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, descricao de poderes e cores e estrutura This is",
    "a1": "presente continuo, aliados, inimigos e motivacoes basicas",
    "a2": "passado simples, historias de origem e comparativos de habilidades",
    "b1": "dilemas, consequencias, voz passiva, verbos modais e articulacao de ideias",
    "b2": "critica de genero, semiotica do heroi e vocabulario analitico",
    "c1": "analise institucional e politica, teoria pos-colonial, etica e registro academico",
    "c2": "registro erudito, ensaio arquetipico e densidade metafisica",
}


class Command(BaseCommand):
    help = "Replace the HQs catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="hqs")
        characters = self.ensure_characters()
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = STORY_TEXTS[level.slug]
            existing = list(
                Text.objects.filter(category=category, level=level)
                .select_related("level", "category", "character")
                .order_by("id")
            )

            for index, (title, character_slug, content) in enumerate(entries, start=1):
                character = characters[character_slug]
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-hqs-{index:02d}-{title}")
                text.title = title
                text.summary_pt = self.summary_for(level, title, content, character)
                text.content_en = content
                text.level = level
                text.category = category
                text.character = character
                text.cover_image = ""
                text.word_count = words
                text.estimated_reading_time = max(1, round(words / 170))
                text.image_prompt = self.prompt_for(level, category, title, content, character)
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} HQs texts."))

    def ensure_characters(self):
        characters = {}
        for name, slug, publisher in CHARACTERS:
            character, _ = Character.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "publisher": publisher,
                    "description_pt": f"Texto original e curto sobre {name}, com abordagem educativa para leitura em ingles.",
                    "is_active": True,
                },
            )
            characters[slug] = character
        return characters

    def summary_for(self, level, title, content, character):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre HQs: {title}. Personagem: {character.name}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content, character):
        scene = content.split(".")[0].strip()
        return (
            "Educational 2D comic-inspired illustration, original and transformative, clean lines, high quality, "
            "no official logos, no copyrighted costume copy, no text inside the image, "
            f"scene about {title}, inspired by the archetype of {character.name}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
