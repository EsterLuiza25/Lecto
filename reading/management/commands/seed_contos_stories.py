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
        "The Red Umbrella",
        "It is a rainy day. Anna walks to the bus stop. She has a big red umbrella. The wind is very strong. Suddenly, the wind takes the umbrella! The red umbrella flies into the sky like a bird. Anna is surprised. She runs after the umbrella, but it is too fast. Now, Anna is wet, but she laughs. Nature is full of surprises.",
    ),
    (
        "The Hungry Cat",
        "Leo is a black cat. He lives in a small apartment. Leo is very hungry today. He looks at his bowl, but it is empty. He meows at the door. His owner, Marco, arrives with a bag. It is cat food! Leo is very happy now. He eats his dinner and sleeps on the sofa. Life is good for a hungry cat with a kind owner.",
    ),
    (
        "The Lost Key",
        "David is at the front door of his house. He looks in his pockets. He looks in his bag. The key is not there! David is worried. He looks under the mat. Nothing. Then, he sees something shiny in the grass. It is the key! David smiles and opens the door. He is finally home. Small things are very important.",
    ),
    (
        "The Blue Bird's Song",
        "Every morning, a small blue bird sits on my window. The bird sings a beautiful song. I listen to the music while I drink my coffee. The song is happy and loud. When the sun is bright, the bird flies away to the forest. I wait for the bird every day. The music of nature is the best way to start the morning.",
    ),
    (
        "A Secret Garden",
        "Behind the old library, there is a small wooden door. Tom opens the door slowly. Inside, there is a secret garden. There are many white flowers and a small fountain. The water is very cold. No one knows about this place. Tom sits on the grass and listens to the water. It is a very quiet and magic place in the city.",
    ),
    (
        "The Big Cake",
        "Today is Maria's birthday. Her mother makes a big chocolate cake. The cake has ten candles. Maria blows out the candles and makes a wish. Her friends clap their hands and sing. Everyone eats a piece of the delicious cake. Maria is very happy. A birthday with a cake and friends is a perfect day.",
    ),
    (
        "The Man and the Moon",
        "Mr. Miller lives in a tall building. Every night, he looks at the moon through his window. The moon is big and white. Mr. Miller thinks about the stars and the planets. He wants to fly in a rocket one day. The night sky is very dark, but the moon is like a lamp. Mr. Miller dreams about the space before he sleeps.",
    ),
    (
        "The Fast Rabbit",
        "A rabbit lives in the green field. He is very fast. He jumps over the rocks and runs under the trees. A slow turtle walks on the path. The rabbit laughs at the turtle. But the turtle is constant. The rabbit stops to sleep, but the turtle continues. Finally, the turtle arrives first. Slow and constant wins the race.",
    ),
    (
        "The New Bicycle",
        "Lucas has a new bicycle. It is blue and silver. Lucas wears a black helmet for safety. He rides his bike in the park every afternoon. The wind is in his face. He feels very fast and free. His father watches him and smiles. Lucas loves his new bicycle. It is his favorite way to explore the neighborhood.",
    ),
    (
        "A Message in a Bottle",
        "Sara is at the beach. She walks near the water. She finds a glass bottle in the sand. Inside the bottle, there is a piece of paper. The paper says: Hello from far away! Sara is very excited. She looks at the ocean and thinks about the person. She decides to write a message too. The ocean connects the world.",
    ),
]


STORY_TEXTS["a1"] = [
    (
        "The Missing Backpack",
        "Yesterday, Leo went to the university library to study for his exam. He put his blue backpack on the chair and went to look for a book about Python. Ten minutes later, he returned to his desk, but the backpack was not there! Leo was very worried. He talked to the librarian and she looked behind the counter. Finally, a girl arrived with the backpack. She said: I took this by mistake, I am very sorry! Leo smiled and felt relieved. It was a stressful morning, but he found his bag and started his studies.",
    ),
    (
        "A Night in the Cabin",
        "Last winter, my friends and I stayed in a small wooden cabin in the mountains. At night, it was very cold and silent outside. First, we made a fire in the fireplace to stay warm. Then, we cooked a simple soup and talked about our favorite movies. Suddenly, we heard a strange noise at the door. We were a bit scared, so we looked through the window. It was only a small deer! The deer looked at us and walked back into the dark forest. We laughed and finally went to sleep. It was a magic night.",
    ),
    (
        "The Surprise Invitation",
        "Two days ago, Clara received a mysterious letter in her mailbox. The envelope was purple and smelled like flowers. Inside, there was an invitation to a secret party at the old museum. Clara was very curious, so she decided to go. She wore her best dress and arrived at the museum at 8 p.m. When she opened the door, all her friends shouted: Surprise! It was not a secret party, but a surprise celebration for her graduation. Clara cried with happiness because she didn't expect such a beautiful gesture from her classmates.",
    ),
    (
        "The Lost Puppy",
        "On Saturday morning, Lucas found a small puppy near the park. The puppy was very small, brown, and very dirty. Lucas decided to help the animal. First, he took the puppy home and gave him a warm bath. Then, he fed him some milk and bread. The puppy felt much better and started to wag his tail. Lucas posted a photo of the dog on social media to find the owner. Two hours later, a neighbor called. She was very happy to find her dog! Lucas was a bit sad to say goodbye, but he was happy to help.",
    ),
    (
        "The First Flight",
        "Last month, Maria traveled by plane for the first time. She was very nervous because she is afraid of heights. At the airport, she checked her bags and waited for the flight. When the plane started to move, she closed her eyes and held her mother's hand. But after ten minutes, she looked through the window. The clouds looked like white cotton and the city was very small. It is beautiful! she said. She enjoyed the rest of the trip and watched a comedy movie. Now, Maria wants to travel to different countries every year.",
    ),
    (
        "The Old Clock",
        "Mr. Peterson bought an old clock at a garage sale last Sunday. The clock was made of dark wood and it didn't work. Mr. Peterson took the clock to his garage and cleaned it carefully. He found a small piece of metal inside the mechanism. He fixed the piece and suddenly, the clock started to tick: Tick, tock, tick, tock. At midnight, the clock played a beautiful melody. Mr. Peterson was very proud of his work. He realized that old things have many stories and sometimes they only need a little bit of love.",
    ),
    (
        "A Day at the Art Gallery",
        "Last Tuesday, my sister and I visited the new art gallery in the city center. We saw many colorful paintings and modern sculptures. One painting was very strange because it only had a big blue circle in the middle. We stayed there for a long time and talked about the meaning of the art. Then, we went to the gallery cafe and drank some hot chocolate. My sister bought a postcard of a landscape to put on her bedroom wall. It was a very inspiring afternoon. I want to start painting again soon.",
    ),
    (
        "The Chef's Mistake",
        "Last night, Daniel cooked dinner for his girlfriend. He decided to make a special pasta with tomato sauce. He was very busy talking on the phone, so he didn't pay attention to the recipe. By mistake, he put sugar in the sauce instead of salt! When they started to eat, the pasta tasted like a dessert. Daniel was very embarrassed and apologized. But his girlfriend laughed and said: It's okay, let's order a pizza! They had a fun night and learned that mistakes in the kitchen can be very funny.",
    ),
    (
        "The Forgotten Umbrella",
        "It started to rain very hard when Sarah left the office. She looked for her umbrella in her bag, but she remembered: I left it on the bus this morning! She was very frustrated. She waited under the roof for twenty minutes. Suddenly, a man she didn't know stopped next to her. He had a very large umbrella. Do you need help? I can walk with you to the subway station, he said. Sarah accepted the help and they talked about the weather. Because of a forgotten umbrella, Sarah made a new friend.",
    ),
    (
        "The Starry Night",
        "When I was a child, my grandfather took me to the backyard every Friday night. We sat on a large blanket and looked at the sky. He showed me the constellations and told me stories about the ancient Greek heroes. Last night, I looked at the stars from my balcony and remembered those moments. The sky was very clear and I saw a shooting star. I made a wish, just like I did twenty years ago. The stars are always there to remind us of our best memories and the people we love.",
    ),
]


STORY_TEXTS["a2"] = [
    (
        "The Quietest Neighbor",
        "Mr. Henderson was the quietest man in the entire building. He lived on the fifth floor, just above my apartment. While other neighbors played loud music or had noisy parties, Mr. Henderson preferred the silence of his books. One evening, while I was studying for my software engineering exam, I heard a very strange sound coming from his kitchen. It was louder and more rhythmic than his usual movements. I was more curious than afraid, so I knocked on his door. When he opened it, I saw the most incredible thing: Mr. Henderson was dancing tango with a professional partner! He was much more energetic than I imagined. He smiled and said that dancing made him feel younger and happier than reading. It was the most surprising discovery of my year. We are now better friends, and sometimes he even teaches me a few steps.",
    ),
    (
        "The Most Beautiful Mistake",
        "Last summer, I planned the most organized trip to the coast. I bought the most expensive tickets and booked the modernest hotel near the beach. However, when I arrived at the station, I realized I took the wrong train. Instead of the sunny beach, I arrived at a small, foggy village in the mountains. At first, I felt angrier than a person in a traffic jam. But then, I walked through the cobblestone streets. The air was fresher and the people were kinder than in the city. I found a small guesthouse that was cheaper and more comfortable than my hotel. I spent the week hiking and drinking the best hot chocolate of my life. That mistake became the most relaxing vacation I ever had. Sometimes, the unplanned path is better than the perfect plan.",
    ),
    (
        "A Competition of Giants",
        "In a small forest, a young oak tree and a tall pine tree had a long argument. The pine tree thought he was the most important because he was taller and greener during the winter. I am more elegant than you, he said to the oak. The oak tree was shorter, but his trunk was much thicker and stronger. One night, the most powerful storm of the decade arrived. The wind was faster than a car and the rain was heavier than a waterfall. The pine tree moved a lot because he was very thin. Suddenly, his top part broke. The oak tree, however, stayed firm because his roots were deeper. The next morning, the pine tree was sadder, but wiser. He realized that being the strongest is often more important than being the tallest.",
    ),
    (
        "The Silver Whistle",
        "When I was younger, my grandfather gave me a silver whistle. He said it was the most powerful object in his collection. I thought it was just a regular toy, but it looked shinier than my other things. One afternoon, while I was playing in the woods, I got lost. The forest was getting darker and colder every minute. I felt more frightened than ever before. I remembered the whistle and blew it as hard as I could. The sound was higher and clearer than a bird's song. A few minutes later, my dog, Max, arrived. He was faster than a lightning bolt! He found me and led me back home. My grandfather was waiting at the door. He told me that the whistle wasn't magic, but the love of a dog is the most reliable map in the world.",
    ),
    (
        "The Chef's New Recipe",
        "Chef Julian wanted to create the most famous dish in Paris. He spent weeks looking for the rarest ingredients. He bought the spiciest peppers from Mexico and the most aromatic herbs from Italy. He thought that a more complex recipe was always better. However, when he served the dish to the most famous food critic, the man looked disappointed. This is too heavy, the critic said. Julian felt more frustrated than a student failing a test. The next day, he decided to try something simpler. He cooked a basic tomato soup with fresh bread. It was the cheapest and easiest meal on his menu. To his surprise, the critic loved it! Julian learned that sometimes, the simplest things are the most delicious.",
    ),
    (
        "The Fastest Delivery",
        "Beto worked as a delivery boy in the busiest part of Sao Paulo. He had the fastest bicycle in the company, but the traffic was always worse than he expected. One Friday night, he had to deliver a large pizza to the most distant neighborhood. He was more tired than usual, but he started pedaling. While he was riding, he saw an old woman trying to cross the street with heavy bags. Beto stopped to help her. He was more helpful than the other drivers who were just honking. Because of his kindness, he arrived ten minutes later than the deadline. He expected the customer to be angrier, but the man was the woman's son! He gave Beto the biggest tip of the month. Being kind was more rewarding than being fast.",
    ),
    (
        "The Old Library's Secret",
        "Our university has the oldest library in the city. The basements are darker and dustier than the study rooms, but they contain the most interesting books. Last Tuesday, while I was looking for a manual about Django, I found a very small book with a gold cover. It was older than any book I saw before. I opened it and found a map of the campus from 1920. I noticed that there was a fountain in the middle of the park that doesn't exist today. I went to the park and looked at the grass. I found a stone that was different from the others. Under the stone, there was a time capsule! It was the most exciting discovery of the semester. The past is often closer than we think.",
    ),
    (
        "A Winter Tale",
        "The winter of 2025 was the coldest in history. The snow was deeper than a person's knees, and the wind was sharper than a knife. My neighbor, Mrs. Rosa, was older and more fragile than the rest of us, so we decided to help her. My brother and I cleared the snow from her path every morning. We were faster and stronger than the other teenagers on the street. Mrs. Rosa was so grateful that she invited us for the best soup I ever tasted. It was warmer and more flavorful than any meal from a restaurant. Although the weather was the worst, the feeling of community was the best. We realized that the hardest times often bring out the most generous parts of people.",
    ),
    (
        "The Most Expensive Painting",
        "An artist named Lucas painted a picture of a single blue drop of water. He thought it was his best work, but the art gallery owners said it was too simple. They preferred bigger and more colorful paintings. Lucas felt more discouraged than a programmer with a bug he can't fix. He decided to sell the painting at a street market for a very low price. A young girl bought it because she thought the blue was the most peaceful color in the world. Ten years later, that girl became a famous collector. She put the painting in a museum. Now, it is one of the most expensive and admired paintings in the country. Lucas learned that the value of art is in the eye of the person who loves it.",
    ),
    (
        "The Smartest Robot",
        "A scientist built two robots: Alpha and Beta. Alpha was the most intelligent because he could solve the most difficult math problems in seconds. Beta was simpler and slower, but he was programmed to be more empathetic. One day, the scientist felt very sad and lonely. Alpha tried to explain the physics of emotions, but his explanation was more confusing than helpful. Beta, however, sat next to the scientist and played a soft melody. The scientist felt much better. He realized that while Alpha was the smartest, Beta was the most valuable companion. Sometimes, a kind heart is more important than the most advanced processor.",
    ),
]


STORY_TEXTS["b1"] = [
    (
        "The Algorithm of Choice",
        "Elias was a brilliant developer who lived for logic. He believed that if he could write a perfect algorithm for his life, he would never make a mistake again. Consequently, he spent his weekends coding a program called The Path. One evening, the program suggested that if he wanted to maximize his productivity, he should stop seeing his friends and focus only on his latest software project. Elias followed the advice, and for a month, his code was flawless. However, he soon realized that he was feeling increasingly miserable. He sat in his dark apartment, staring at a perfect screen, but feeling a profound emptiness. He finally understood that while logic is essential for machines, human happiness is often found in the bugs-the unpredictable moments shared with people. He deleted the program and called his best friend. If I had known that perfection was this lonely, he said, I would have chosen the chaos much sooner.",
    ),
    (
        "The Echo of the Old Piano",
        "In a dusty corner of an antique shop, there was an old piano that no one wanted to buy because its wood was scratched and its keys were yellow. One rainy afternoon, a young woman named Clara entered the shop. She sat at the piano and began to play a melody that sounded like a conversation between two old friends. As she played, the other customers stopped to listen. The shop owner was surprised because he had thought the instrument was broken. Clara explained that if you treat an old object with respect, it will share its history with you. Consequently, the shop owner decided not to sell the piano, but to keep it as a centerpiece for the community. Clara's music proved that the value of an object is not in its appearance, but in the emotions it can evoke. Therefore, the shop became a place where people gathered not just to buy things, but to listen to the echoes of the past.",
    ),
    (
        "The Stranger's Umbrella",
        "If Julian hadn't missed his bus that morning, he never would have met the woman with the green umbrella. It was pouring rain, and he was standing under a small roof, feeling frustrated about being late for work. Suddenly, a woman stopped beside him and offered to share her umbrella. As they walked toward the subway, they started talking about their careers. Julian discovered that she was a senior architect at a firm he had always admired. Consequently, by the time they reached the station, she had given him her business card and suggested he apply for a new position. If Julian had caught his bus, he would have spent the day in a boring office. Instead, a simple act of kindness from a stranger changed his entire professional trajectory. This taught Julian that sometimes, a failure in our routine is actually an opportunity in disguise.",
    ),
    (
        "The Garden of Second Chances",
        "After retiring, Mr. Silva bought a house with a garden that was completely dead. His neighbors told him that the soil was too poor for anything to grow. However, Mr. Silva believed that if he worked hard enough, he could bring the land back to life. Every morning, he spent hours removing rocks and adding natural compost. Consequently, by the following spring, small green shoots began to appear. People were amazed to see roses and lavender blooming in a place that used to be a desert. Mr. Silva explained that nature, like people, sometimes just needs a second chance and a bit of patience. Because he didn't give up, his garden became the most beautiful spot in the neighborhood. Therefore, it served as a reminder to everyone that if you invest love into something, even the most broken things can flourish again.",
    ),
    (
        "The Silent Librarian",
        "Miss Evelyn had worked at the city library for forty years. She was famous for being extremely strict about silence. If someone whispered, she would immediately point to the Shh! sign. Most students were afraid of her, but one boy named Samuel noticed that she spent her lunch breaks reading books about far-off galaxies. One day, he brought her a photograph of a nebula he had taken with his telescope. Consequently, Miss Evelyn's eyes lit up, and she began to tell him about her dream of being an astronomer. If Samuel hadn't looked past her stern exterior, he would have never known she was a dreamer. They became unlikely friends, and Samuel realized that people often build walls of silence to protect their most precious thoughts. Therefore, he learned that the most interesting stories are often hidden behind the quietest faces.",
    ),
    (
        "The Map to Nowhere",
        "While cleaning his grandfather's attic, Tomas found a map that didn't show any cities or roads. Instead, it was filled with drawings of trees, rivers, and mysterious symbols. Curious, he decided to follow the map into the local forest. If he had used a GPS, he would have stayed on the main path, but the map led him through thick bushes and hidden valleys. Consequently, he discovered a breathtaking waterfall that was not on any official map of the region. He spent the afternoon listening to the water and feeling a peace he had never felt in the city. He realized that if we only follow the paths made by others, we will never find anything truly new. Therefore, the map to nowhere was actually a guide to finding himself.",
    ),
    (
        "The Baker's Secret Ingredient",
        "Everyone in the village wondered why Elena's bread was the best in the country. Some thought she used a secret spice, while others believed her oven was magical. One day, a young apprentice asked her for the secret. Elena smiled and said, If I told you it was just flour and water, you wouldn't believe me. She explained that the secret was actually the time she spent kneading the dough. If she was in a hurry, the bread was average. But if she sang and took her time, the bread was perfect. Consequently, the apprentice learned that quality cannot be rushed. Because Elena put her heart into her work, the bread fed more than just people's hunger; it fed their souls. Therefore, the secret ingredient wasn't a substance, but an attitude toward life.",
    ),
    (
        "The Watchmaker's Warning",
        "In a small town in the Alps, there lived a watchmaker who claimed he could fix time itself. One day, a man arrived and asked the watchmaker to speed up his watch because he was always late and stressed. The watchmaker warned him, If I make your watch faster, your life will feel shorter. You will reach your goals quickly, but you will miss the journey. The man didn't listen and insisted on the change. Consequently, a month later, he returned, looking exhausted. He said that although he was never late, he felt like he was constantly running and couldn't enjoy his family or his meals. He asked the watchmaker to set the time back to normal. Therefore, he understood that if we try to control time, we often lose the moments that make time worth having.",
    ),
    (
        "The Lighthouse Keeper's Daughter",
        "Maya lived in a lighthouse on a rocky island. Her father always told her that if the light went out, the ships would be in great danger. Consequently, Maya grew up with a deep sense of responsibility. One night, a violent storm broke the main lantern. Her father was injured, so Maya had to climb the tall tower alone. If she had been afraid of the heights or the wind, she would have failed. Instead, she focused on the light and managed to fix the mechanism just as a large ship was approaching the rocks. The ship saw the signal and turned away just in time. Therefore, Maya realized that bravery isn't the absence of fear, but the decision that something else is more important than fear.",
    ),
    (
        "The Writer's Block",
        "Juliana was a writer who couldn't finish her book. She sat at her desk for weeks, but the pages remained white. She thought that if she stayed in her room, the inspiration would eventually come. However, she was wrong. One day, she decided to leave her apartment and walk through the local market. She listened to the conversations, smelled the spices, and watched the colors of the sunset. Consequently, her mind began to fill with ideas. She realized that if a writer doesn't live, a writer has nothing to say. Because she stepped out into the world, her story finally found its ending. Therefore, she learned that creativity isn't a resource you find inside yourself, but a reaction to the beauty of the world around you.",
    ),
]


STORY_TEXTS["b2"] = [
    (
        "The Weight of a Secret",
        "Arthur was a respected archivist who had spent his entire career protecting the history of his city. One afternoon, while digitizing a collection of private letters from the 1920s, he discovered a document that proved the city's most beloved founder had actually built his fortune through corruption and theft. Arthur realized that if this information were released, it would destroy the reputation of a man who was considered a hero. Consequently, he faced a profound ethical dilemma. He told his colleague, Sarah, that he had found something disturbing, but he didn't reveal the details. Sarah argued that the truth was always the most important thing, regardless of the consequences. However, Arthur worried that the truth might cause more harm than good to the community's spirit. If he had never found the letter, his conscience would be clear. Now, he felt as if he were carrying the weight of the entire city's history on his shoulders. In the end, he decided that a society built on lies is fragile, and he prepared the document for publication, knowing his own life would never be the same.",
    ),
    (
        "The Mirror of Truth",
        "In a forgotten village in the mountains, there was a legend about a mirror that didn't show your face, but your true character. If you were a generous person, the mirror was said to shine like gold; however, if you were selfish, it would look like cold, dark stone. A wealthy merchant named Silas, who was famous for his greed, decided to find the mirror to prove the legends were false. He told his servants that he wasn't afraid of a piece of glass. After a long journey, he found the mirror in an ancient temple. When he stood before it, he expected to see a reflection of his power and gold. Instead, the mirror turned into a deep, black void. Silas was told by an old monk that the mirror only reflected what was inside the soul. Consequently, Silas returned to his village and began to give his wealth to the poor. He realized that if he hadn't seen his own emptiness, he would have died a rich but hollow man. The mirror didn't change his face, but it certainly changed his life.",
    ),
    (
        "The Clockmaker's Last Request",
        "Old Elias was the most talented clockmaker in the country. Before he died, he left a mysterious wooden box to his apprentice, Thomas. He told Thomas that the box contained the heart of time and warned him never to open it unless he truly understood the value of a second. Thomas was more curious than wise, and he spent years trying to figure out the mechanism. He often complained that if he had more time, he would be the greatest master in Europe. Eventually, his obsession with the box caused him to ignore his family and his friends. On his 80th birthday, he finally managed to open it. Inside, there was no magic machinery, only a small mirror and a note that said: Time is not inside a box; it is what you see in the mirror every morning. Thomas realized, with great sadness, that while he had been searching for the secret of time, he had let his own life slip away. If he had listened to the master's warning, he would have spent those years living instead of searching.",
    ),
    (
        "The Invisible Thread",
        "Elena was a talented weaver who believed that every person was connected to others by an invisible thread. She told her daughter that if you hurt someone, you were actually pulling on your own thread, causing a knot in your own heart. One day, a rival weaver started spreading lies about Elena's work to steal her customers. Elena was tempted to seek revenge and tell the village about the rival's own mistakes. However, she remembered her own philosophy. She decided that if she responded with anger, she would only become like the person who hurt her. Consequently, she continued to weave her beautiful fabrics with patience and kindness. Eventually, the truth came out, and the rival was forced to leave the village in shame. Elena's daughter asked her why she hadn't fought back. Elena replied that the thread of peace was more valuable than the satisfaction of revenge. By choosing silence, she had kept her own heart free from knots.",
    ),
    (
        "The Library of Unwritten Books",
        "Julian discovered a hidden door in the university library that led to a room filled with blank journals. An old librarian told him that this was the Library of Unwritten Books-stories that people had thought of but never had the courage to write. Julian found a book with his own name on it. When he opened it, he saw titles of novels he had dreamed of writing during his software engineering classes but had put aside because he was too busy. He was told that if he didn't start writing soon, the pages would remain blank forever. The experience was a profound shock to his system. He realized that he had been prioritizing a career he didn't love over a passion that defined him. Consequently, he bought a pen and started writing the first chapter of his life. He understood that the greatest tragedy isn't failing, but never having the courage to begin.",
    ),
    (
        "The Captain's Choice",
        "During a violent storm at sea, Captain Miller had to make a choice that would haunt him for the rest of his life. His ship was sinking, and there was only one lifeboat left. He told his crew that the women and children must go first, as per the maritime tradition. However, one young sailor begged to stay, saying that he was the only one who could navigate the boat through the rocks. The Captain was told by his first mate that if the sailor didn't go, the lifeboat might not survive the waves. Miller had to decide between following the rules or ensuring survival. He chose to put the sailor on the boat. Years later, he was questioned by a court about his decision. He admitted that while he had broken the rules, he had saved twenty lives. He realized that in extreme situations, morality isn't a fixed line, but a heavy burden of responsibility.",
    ),
    (
        "The Gift of the Flute",
        "A traveling musician once gave a wooden flute to a young boy who was born mute. The musician told the boy that if he played with his heart, the flute would speak the words he couldn't say. The boy practiced every day in the forest, and soon, the music he produced was more beautiful than any human voice. People from all over the country came to hear him play. He was told by a wealthy king that if he moved to the palace, he would never be hungry again. The boy was tempted, but he realized that his music was a gift for everyone, not just for the powerful. He decided to stay in his village and play for the farmers and the children. He understood that if he had sold his talent, the flute would have lost its magic. True wealth, he discovered, is the ability to touch the hearts of others without asking for anything in return.",
    ),
    (
        "The Alchemist's Failure",
        "Master Alchemist Valerius had spent forty years trying to turn lead into gold. He told his pupils that if they were disciplined enough, they would eventually unlock the secrets of the universe. One day, he finally produced a small piece of shining metal. However, as he looked at the gold, he felt a strange sense of disappointment. He realized that the gold was cold and lifeless, while the flowers in his garden were vibrant and full of energy. He was told by a visiting philosopher that the search for gold was actually a search for immortality, which is impossible. Valerius looked at his worn hands and his gray hair. He understood that the real alchemy was the transformation of a selfish heart into a wise one. He threw the gold into the river and spent the rest of his days teaching his students how to appreciate the beauty of the temporary.",
    ),
    (
        "The Painting that Changed Color",
        "There was a painting in the city hall that was said to change color depending on the honesty of the government. If the leaders were fair, the landscape was bright and sunny; if they were corrupt, the sky in the painting turned gray and stormy. A new mayor arrived and noticed that the painting was looking particularly dark. He was told by his advisors that the painting was just old and needed cleaning. However, the mayor suspected that the problem was deeper. He began to investigate the city's finances and discovered that his predecessors had been stealing from the public funds. As he started to fix the problems and return the money, the painting gradually became brighter. He realized that the art was a reflection of the collective conscience of the city. If he hadn't been brave enough to look at the gray sky, the city would have remained in the dark forever.",
    ),
    (
        "The Architect of Dreams",
        "An architect was hired to build a prison, but he decided to design it as a school instead. He told the city council that if people were given light and books, they wouldn't need bars and cells. The council was skeptical and told him that his plan was too idealistic. However, the architect insisted that the environment shaped the behavior of the inhabitants. He built the structure with large windows, gardens, and open spaces. Ten years later, the crime rate in the city had dropped significantly. The council admitted that the architect had been right all along. He realized that his work wasn't just about stone and glass, but about the potential of the human spirit. If he had built the prison as requested, he would have contributed to the problem instead of the solution. Architecture, he believed, should always be a tool for liberation.",
    ),
]


STORY_TEXTS["c1"] = [
    (
        "The Cartographer of Memories",
        "In a metropolis where history was rewritten by the hour to suit the whims of a nebulous Council of Progress, Elias occupied a perilous position: he was a cartographer of memories. His task was not to map physical geography, but to document the subjective emotional landscapes of a citizenry increasingly afflicted by a collective amnesia. Were it not for his meticulous records, the city would have entirely lost its connection to the Old World-a time before the algorithms dictated the rhythm of human affection. One afternoon, Elias encountered a woman who claimed to remember the exact scent of rain on dry pavement, a sensory detail long ago purged from the official archives. As he interviewed her, he realized that her memory functioned as a form of rebellion; by remembering the past, she challenged the Council's monopoly on the present. Had Elias been a loyal servant of the state, he would have reported her immediately. Instead, he found himself complicit in her subversion, recognizing that the most accurate maps are those that trace the contours of what has been forgotten.",
    ),
    (
        "The Silence of the Symphony",
        "The Great Concert Hall was a triumph of brutalist architecture, designed to amplify sound to its most visceral intensity. However, the celebrated composer, Julian Vane, had recently become obsessed with the aesthetics of absence. He argued that in a world saturated with noise, the ultimate artistic statement was not sound, but the deliberate curation of silence. For his final performance, Vane instructed the orchestra to sit in perfect stillness for forty minutes. To the audience, this was initially perceived as a provocation, yet as the minutes passed, the collective discomfort shifted into a profound awareness of their own biological presence-the rustle of fabric, the rhythm of breath, the distant hum of the city. Vane proposed that only through the suspension of the expected could the audience truly hear the unheard. Consequently, the performance became a psychological mirror, forcing the listeners to confront the void within themselves. To understand the symphony, one had to first survive the silence.",
    ),
    (
        "The Ethics of the Simulacrum",
        "As an expert in predictive middleware and AI-driven behavioral anomalies, Dr. Aris dealt with the blurred lines between data and soul. He was tasked with overseeing the Reintegration Program, where digital facsimiles of deceased individuals were integrated back into the lives of their mourning families. The nuance of his dilemma lay in the authenticity of grief; if a family found solace in a simulation, did the technological nature of that comfort diminish its emotional validity? Aris observed that the more perfect the AI became, the more the families drifted away from their own reality, preferring the predictable digital ghost to the messy, unpredictable nature of living relationships. He realized that the simulacrum was not a bridge to memory, but a tomb for the future. Were he to shut down the program, he would cause a second, perhaps more devastating, wave of grief. Yet, to allow it to continue was to facilitate a collective retreat into a synthetic past.",
    ),
    (
        "The Library of Whispers",
        "Hidden beneath the crust of an ancient university lay the Library of Whispers, a sanctuary for books that were deemed too dangerous to be read, yet too precious to be burned. The librarian, a woman who had long ago traded her sight for a heightened sense of intuition, claimed that the books spoke to those who knew how to listen to the spaces between words. She told a young scholar that every written thought carried a temporal residue-a weight that could alter the reader's perception of reality. The scholar, eager to solve a historical mystery, sought a manuscript that supposedly detailed the End of Time. However, the librarian warned him that to read the book was to accept its conclusion as your own. In the library, knowledge was not a commodity to be acquired, but a transformative force that demanded a price. Only those who understood that truth is a double-edged sword were permitted to leave with their minds intact.",
    ),
    (
        "The Architect of the Invisible City",
        "An architect was commissioned to build a structure that would represent the peak of his civilization's achievement. Instead of using steel and glass, he proposed a city built entirely of intentionality and light. He argued that physical structures were merely temporary manifestations of human desire, and thus, were destined to decay. By creating a city through the collective imagination of its inhabitants, he sought to build something eternal. The city council, obsessed with physical symbols of power, viewed his proposal as madness. Yet, as the architect began to build through stories, shared dreams, and rituals, the people started to inhabit this invisible space, finding more meaning in the unseen city than in their concrete homes. The architect realized that true architecture is not about the construction of space, but about the elevation of the human spirit. If the physical city fell, the invisible one would endure, proving that the strongest foundations are those laid in the soul.",
    ),
    (
        "The Alchemist's Penance",
        "In a world where alchemical transmutations were used to fuel the engines of industry, a former master of the craft lived in self-imposed exile. He had once been the architect of the Golden Age, a period where he successfully converted lead into a fuel that powered an entire continent. However, he soon discovered that the alchemical process extracted a hidden cost from the very fabric of the earth, leading to the slow, irreversible decay of the natural world. His penance was to spend his remaining years trying to reverse the transmutation-to turn the gold back into the humble lead. His peers viewed his efforts as a tragic waste of talent, unable to perceive the slow catastrophe he had unleashed. The alchemist understood that progress at the expense of the earth is a form of spiritual bankruptcy. His story serves as a cautionary tale: the most dangerous alchemy is the belief that we can exploit the finite to achieve the infinite.",
    ),
    (
        "The Semiotics of the Mask",
        "The Masquerade of the High Nobles was an annual event where identity was legally suspended for twenty-four hours. Behind elaborate masks of silver and bone, political rivals shared secrets and enemies became lovers. The nuance of the event was the truth through artifice; because no one was who they seemed, everyone felt free to speak with a brutal honesty that was impossible in daily life. A young diplomat, attending for the first time, realized that the masks did not conceal their faces, but rather revealed their hidden desires. He observed that the most authentic version of his colleagues appeared only when they were disguised. This paradox suggested that social identity is itself a mask, a performance constructed to satisfy the expectations of the collective. To remove the mask was not to find the true self, but to lose the only shield one had against the crushing weight of public persona.",
    ),
    (
        "The Watchmaker's Paradox",
        "A watchmaker was tasked with repairing a clock that supposedly governed the flow of time in a remote mountain village. The villagers believed that if the clock stopped, time itself would cease to exist for them. Upon opening the mechanism, the watchmaker discovered that the gears were not connected to anything; the clock was a magnificent piece of theater with no functional core. He realized that the villagers' belief in the clock was what actually regulated their lives, creating an orderly flow of existence through a shared fiction. He faced a choice: reveal the deception and risk the collapse of the village's social structure, or maintain the illusion and continue the lie. He decided to fix the clock by adding new, equally non-functional gears. He understood that in a world of chaos, people require a sacred mechanism-even a false one-to maintain the illusion of control over the entropic nature of time.",
    ),
    (
        "The Garden of Bifurcating Paths",
        "A philosopher spent his life cultivating a garden where the paths were designed to represent the various turning points of human history. Each choice a visitor made led to a different narrative conclusion, illustrating the concept of contingent reality. A young soldier, traumatized by the wars of his era, visited the garden to find a path where the conflict had never happened. The philosopher told him that while the garden contained all possibilities, the visitor could only inhabit one. The nuance of the lesson was that regret is the refusal to accept the path one is currently on. The soldier realized that looking for a better past was a form of self-inflicted torment. By accepting the path of the survivor, he found a peace that had previously eluded him. The garden taught him that while we cannot change the choices of the past, we have the absolute agency to define the meaning of the present.",
    ),
    (
        "The Last Lexicographer",
        "As language became increasingly simplified and reduced to emojis and corporate jargon, a lone lexicographer dedicated her life to preserving lost words-terms for emotions and phenomena that no longer had a place in the modern mind. She argued that when a word dies, the experience it describes becomes inaccessible to the human heart. Her dictionary was a cemetery of nuance, containing words for the specific melancholy of a dying star or the joy found in a stranger's success. She was told by the Ministry of Efficiency that her work was obsolete, a relic of an inefficiently complex past. Yet, she persisted, recognizing that a world with fewer words is a world with less feeling. Her dictionary was not just a list of definitions, but a manual for reclaiming the full spectrum of human experience. To lose your language, she believed, was to lose your capacity for the infinite.",
    ),
]


STORY_TEXTS["c2"] = [
    (
        "The Mnemosyne Engine",
        "In the twilight of a civilization that had outsourced its collective memory to a decentralized silicon hive, there remained a singular archivist named Valerius, who curated what he termed The Mnemosyne Engine. This was not a mechanical device, but a rigorous mental discipline designed to preserve the qualia of human experience-the irreducible, subjective textures of reality that the algorithms found mathematically redundant. Valerius argued that when a memory is digitized, it undergoes an ontological flattening; the scent of rain or the visceral sting of a betrayal is reduced to a binary state, stripped of its temporal resonance. Consequently, the citizenry lived in a state of perpetual presentism, untethered from the ancestral wisdom of their own history. Valerius's rebellion was an act of mnemic restoration, a desperate attempt to re-internalize the past through oral tradition and sensory ritual. He understood that a species without a private, un-indexed memory is not a collective, but a mere data set. To remember was to claim sovereignty over one's soul in an age of algorithmic enclosure.",
    ),
    (
        "The Cartography of the Invisible",
        "The Great Library of Alexandria, in its fourth and most secretive iteration, contained a series of maps that depicted not the physical world, but the geography of intention. These charts traced the trajectories of unfulfilled desires, the boundaries of silent grief, and the topography of collective dreams. The Head Cartographer, a man whose eyes had been blinded by the sheer intensity of his inner vision, claimed that the visible world was merely a tenuous veil draped over a far more complex, multidimensional reality. He argued that to navigate the city of man, one must first master the city of the spirit. The nuance of his work lay in the shifting borders of these maps; as a society's values evolved, the spiritual coastline would recede or expand. His maps were a critique of the materialist fallacy-the belief that what cannot be measured does not exist. In the end, he proposed that we are all travelers in an invisible landscape, and our tragedies stem from the refusal to acknowledge the terrain of the heart.",
    ),
    (
        "The Dialectics of the Ruin",
        "In a valley where the remnants of a high-tech metropolis were being slowly devoured by an ancient, indifferent rainforest, a philosopher-in-exile sat among the crumbling pillars of a data center. He contemplated the dialectics of the ruin-the process through which human artifice is reabsorbed into the biological absolute. He observed that the decay of a structure is not a loss of form, but a return to a more profound, entropic order. The rust on the steel and the vines strangling the concrete were not enemies of architecture, but its final, inevitable completion. The philosopher argued that the hubris of modern engineering lay in its pursuit of permanence, a categorical error that ignored the rhythmic, cyclical nature of the earth. In the ruin, the distinction between the made and the grown dissolves, creating a liminal space where the past and the future coexist in a state of quiet, moss-covered stasis. To understand the ruin is to accept the finitude of human ambition and the eternal sovereignty of the green world.",
    ),
    (
        "The Semiosis of the Shroud",
        "The legendary Weaver of Isfahan was said to produce a fabric so delicate that it was visible only to those who had experienced a true epiphany. This Shroud of the Infinite was not woven from silk or wool, but from the semantic connections between disparate human lives. The Weaver claimed that every interaction, every shared gaze, and every whispered secret added a thread to the cosmic tapestry. The nuance of this semiosis lay in the negative space between the threads-the silences and the missed opportunities that gave the shroud its structural integrity. To the uninitiated, the Weaver appeared to be working with empty hands, but to the enlightened, he was constructing the very fabric of social reality. The Shroud was a metaphor for the interconnectedness of all things, a reminder that we are not isolated nodes, but woven into a continuous, albeit invisible, narrative. To tear the shroud was to commit an act of ontological violence against the collective being.",
    ),
    (
        "The Epistemology of the Mirror",
        "In a hall of mirrors designed by a mad mathematician, the reflections did not merely replicate the subject; they anticipated the subject's future possibilities. One mirror showed the man he might have been had he chosen a life of quiet scholarship; another reflected the tyrant he would become if he surrendered to his current ambitions. The nuance of this epistemological trap was the psychological fragmentation it induced; the man could no longer identify his true self amidst the cacophony of his potential iterations. He realized that the self is not a fixed essence, but a precarious synthesis of choices and circumstances. The mirrors forced a confrontation with the horror of the possible, the realization that within the individual lies a multitude of irreconcilable ghosts. To escape the hall, he had to close his eyes and trust in the non-reflective reality of his own breath-the only thing that remained constant across all possible worlds.",
    ),
    (
        "The Alchemical Transmutation of Time",
        "The Last Alchemist of Prague did not seek to turn lead into gold, but to convert chronological time into kairological meaning. He argued that the modern obsession with the clock was a form of temporal enslavement, a reduction of the infinite flow of existence into quantifiable, commodified units. Through a series of linguistic and meditative transmutations, he sought to expand the now into an eternal presence. The nuance of his alchemy lay in the stillness of the moment; by stripping away the anxieties of the future and the regrets of the past, he revealed the crystalline beauty of the absolute present. His peers viewed his work as a retreat into mysticism, failing to perceive that he was attempting to heal the fractured consciousness of a society that lived everywhere but in the current moment. His Great Work was the restoration of the sacred time, where every second was an infinity unto itself.",
    ),
    (
        "The Theology of the Coda",
        "A dying composer spent his final hours writing a Coda to the Cosmos, a piece intended to resolve the discordant themes of human existence. He believed that the universe was a grand, unfinished symphony, and that his task was to provide the final, perfect cadence that would imbue the preceding chaos with a retrospective meaning. The nuance of his theology lay in the dissonance of the divine-the realization that the suffering and the beauty of life were inextricably linked, each requiring the other for its emotional weight. As he wrote the final notes, he understood that the resolution was not a cessation of sound, but a transition into a deeper silence. The Coda was an act of existential reconciliation, a peace offering to a world that had offered him both profound joy and unbearable sorrow. In the end, he realized that the music does not stop; it merely changes its key, resonating forever in the architecture of the void.",
    ),
    (
        "The Phenomenology of the Mask",
        "In a society where faces were considered obscene and masks were legally mandated from birth, a rogue artist began to paint portraits of the unmasked. These were not literal depictions of features, but phenomenological mappings of the internal state. He argued that the mask was the true face-the social construct that allowed for communal life-while the face itself was a raw, chaotic landscape of unmediated desire. The nuance of his work was the erasure of the boundary; by depicting the interiority of the subject, he revealed that the mask and the face were a single, continuous surface. The citizenry, horrified by the vulnerability of his portraits, viewed his art as a form of social pornography. Yet, the artist persisted, recognizing that to be truly seen is the ultimate human longing, and the ultimate human terror. The mask was a shield against the devastating intensity of being.",
    ),
    (
        "The Watchmaker's Lamentation",
        "The master watchmaker of the royal court was tasked with creating a clock that would never lose a second over a thousand years. He succeeded in building a masterpiece of astronomical precision, but as he watched the gears turn, he was overcome by a profound lamentation. He realized that in achieving perfect time, he had created a cold, sterile monument to mortality. The nuance of his grief lay in the beauty of the error-the small, human inconsistencies that give life its texture and its unpredictability. He understood that a world without drift is a world without growth. In an act of quiet sabotage, he introduced a microscopic flaw into the mainspring, ensuring that the clock would eventually, inevitably, falter. This gift of imperfection was his final legacy, a reminder that the most valuable things in the universe are those that are subject to the transformative power of decay.",
    ),
    (
        "The Last Lexicographer's Eulogy",
        "As the global lexicon collapsed into a series of functional signals and emotional icons, the last lexicographer began to write a Eulogy for the Nuance. Her work was a profound defense of the untranslatable-the specific, subtle words for feelings that had no place in the streamlined discourse of the hyper-efficient world. She argued that when a word dies, a specific capacity for human emotion dies with it. The nuance of her struggle was the linguistic archaeology she performed, excavating terms for the melancholy of a summer's end or the joy of a shared silence. She recognized that a simplified language leads to a simplified soul. Her dictionary was a fortress of the spirit, a sanctuary for the complexity of the human heart. To lose the word was to lose the world, and her final entry was a definition of hope: the belief that language can still bridge the infinite gap between two solitary minds.",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, estruturas narrativas basicas e vocabulario do dia a dia",
    "a1": "passado simples, conectores de sequencia e historias lineares",
    "a2": "passado simples e continuo, comparativos, superlativos e reviravoltas simples",
    "b1": "dialogos, reflexoes, causa e consequencia, if-clauses e conectores logicos",
    "b2": "dilemas morais, discurso indireto e vocabulario abstrato",
    "c1": "narrativas psicologicas, critica sistemica e linguagem literaria figurada",
    "c2": "registro erudito, narrativas fenomenologicas e alta densidade literaria",
}


class Command(BaseCommand):
    help = "Replace the Contos catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="contos")
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
                text.slug = slugify(f"{level.slug}-contos-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Contos texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles de conto curto: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D storybook style, clean lines, high quality, "
            f"educational short story scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
