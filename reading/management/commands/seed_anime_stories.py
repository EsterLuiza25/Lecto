import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


ANIME_TEXTS = {}


ANIME_TEXTS["iniciante"] = [
    (
        "The Blue Cat",
        "This is Doraemon. He is a blue cat from the future. Doraemon has a magic pocket with many gadgets. He helps a boy named Nobita every day. Doraemon is very kind and funny. I like the stories because they are happy. Anime is a very popular style of animation from Japan. Doraemon is a classic character.",
    ),
    (
        "A Ninja Boy",
        "Naruto is a young ninja. He has orange clothes and yellow hair. He lives in a small village. Naruto wants to be the leader of the village. He practices his skills every morning with his friends. The story is about courage and hard work. I watch Naruto on the weekend. It is a very exciting anime.",
    ),
    (
        "The Magic Forest",
        "In this anime, two sisters move to a new house. They find a big, gray spirit in the forest. His name is Totoro. Totoro is very soft and friendly. He helps the girls when they are sad. There are many magical creatures in the trees. I love this movie because the nature is beautiful. Totoro is my favorite spirit.",
    ),
    (
        "The Red Robot",
        "Astro Boy is a famous robot. He is very strong and fast. He has red boots and black hair. Astro Boy fights for justice and peace. He is like a human boy, but he is made of metal. Many children in Japan love this story. It is a very old and important anime. Robots are cool and helpful.",
    ),
    (
        "Watching Anime at Night",
        "I like to watch anime at night on my computer. I use my headphones because the music is very good. My favorite genre is Slice of Life. These stories are about school, friends, and family. They are very quiet and relaxing. I learn some Japanese words when I watch anime. It is a fun hobby for me.",
    ),
    (
        "A Girl and a Dragon",
        "Chihiro is a small girl in a magic world. She meets a boy named Haku. Haku can transform into a beautiful white dragon. They fly in the blue sky together. The world is full of strange spirits and magic. Chihiro is very brave. This anime movie is famous all over the world. The art is perfect.",
    ),
    (
        "Pokemon Training",
        "Ash is a boy with a yellow friend. His friend is Pikachu. Pikachu can use electricity. They travel to many cities to find new monsters. These monsters are called Pokemon. Ash wants to be a master. They are very good friends. Pokemon is a game and also a very popular anime for kids and adults.",
    ),
    (
        "The School Club",
        "Five girls are in a music club at school. They play the guitar, the drums, and the piano. They drink tea and eat cake every afternoon. Their music is very happy and fast. They are best friends. I like this anime because it is simple and fun. School life in Japan looks very interesting in the animation.",
    ),
    (
        "Super Powers",
        "In this world, many people have super powers. They go to a special school to be heroes. The students wear colorful uniforms. They practice their powers every day. My favorite hero is very strong and fast. They fight bad people to protect the city. Action anime is very popular and full of energy.",
    ),
    (
        "Drawing Manga",
        "Manga is the name for Japanese comics. I like to draw manga characters in my notebook. I draw big eyes and colorful hair. It is not easy, but I practice every day. Some people read manga and then watch the anime on TV. The drawings are very detailed. I want to be an artist one day. Art is magic.",
    ),
]


ANIME_TEXTS["a1"] = [
    (
        "The World of Shonen Anime",
        "Shonen is a very popular genre of anime for young boys, but many girls like it too. These stories usually have a lot of action, adventure, and strong friendships. For example, Dragon Ball and One Piece are classic Shonen titles. In these series, the main character is often a brave boy who trains very hard to protect his friends. I like Shonen because the battles are exciting and the characters never give up. Every week, I wait for the new episode because I want to see the hero get stronger. It is my favorite way to spend my Friday nights.",
    ),
    (
        "Relaxing with Shojo Stories",
        "When I want to relax after a difficult day at the university, I watch Shojo anime. Shojo is a genre specifically for young girls, and it focuses on emotions, romance, and school life. The art style is usually very beautiful, with many flowers and soft colors. Sailor Moon is the most famous Shojo anime in history. The stories are often about a girl who falls in love or finds a magic power. I think Shojo is great because it helps me understand different feelings. Sometimes I watch these series with my friends and we talk about the characters for hours.",
    ),
    (
        "The Life of an Otaku",
        "In Japan, a big fan of anime and manga is called an Otaku. I consider myself an Otaku because I have a large collection of figures and posters in my bedroom. Every morning, I check the news online to see which new series are coming in the next season. Then, I read some chapters of my favorite manga on my tablet. On weekends, I sometimes go to anime conventions in the city. There, I see many people in cosplay, wearing costumes of their favorite characters. Being a fan is fun because I can share my passion with a large community.",
    ),
    (
        "The Mystery of Seinen Anime",
        "Seinen is a genre for older audiences, usually for men over eighteen years old. These stories are more complex and serious than Shonen. They often discuss psychological themes, politics, or dark mysteries. An example of a great Seinen is Monster or Vinland Saga. The characters are not always heroes; sometimes they are very complicated people who make difficult choices. I am currently watching a Seinen about a detective, and it is very intelligent. I prefer this genre when I want to watch something more mature and realistic. It is a very deep style of storytelling.",
    ),
    (
        "Watching Seasonal Anime",
        "Every year, there are four seasons of anime: Winter, Spring, Summer, and Autumn. In each season, many new series start on television and streaming platforms. At the beginning of the season, I read the descriptions and watch the trailers. Then, I choose three or four shows to follow every week. Right now, I am watching a fantasy anime about a dragon and a small comedy about a cat. It is very exciting to wait for a new episode every Saturday morning. Seasonal anime keeps the community busy because everyone is talking about the same shows at the same time.",
    ),
    (
        "The Art of Studio Ghibli",
        "Studio Ghibli is a very famous animation studio in Japan. They make movies that are famous for their incredible art and deep messages. The director, Hayao Miyazaki, creates magical worlds with spirits, flying machines, and strong female characters. My favorite movie is My Neighbor Totoro, but I also love Spirited Away. The music in these films is also very beautiful and relaxing. Many people think Ghibli movies are only for children, but they are actually for everyone. When I watch a Ghibli movie, I feel like I am in a dream. The quality of the animation is perfect.",
    ),
    (
        "Learning Japanese with Anime",
        "One reason why I watch anime is because I want to learn some Japanese words. When I watch with subtitles, I listen to the original voices. I already know simple words like Arigato, thank you, and Ohayou, good morning. Sometimes, the characters use honorifics like -san or -kun after their names to show respect. This is very interesting because it teaches me about Japanese culture. Of course, I cannot speak Japanese yet, but I can understand some basic phrases. Watching anime is a fun and natural way to practice a new language every day.",
    ),
    (
        "The Soundtrack of Anime",
        "The music in an anime is just as important as the animation. Every show has an Opening, or OP, at the start and an Ending, or ED, at the finish. These songs are often very catchy and performed by famous Japanese bands. Sometimes, I download the soundtracks to my phone so I can listen to them while I am coding or walking. A good soundtrack can make a battle scene more epic or a sad moment more emotional. I really like the rock songs in action anime. Music is a big part of why anime is so popular around the world.",
    ),
    (
        "Sports Anime Motivation",
        "I never liked volleyball or basketball in school, but after watching some sports anime, I am very interested! These shows, like Haikyuu!! or Slam Dunk, are not just about the game. They are about teamwork, practicing hard, and reaching your goals. The characters are very motivated, and their energy is contagious. After I watch an episode, I feel like I want to go to the gym or go for a run. It is amazing how an animation about sports can be so inspiring for my real life. Now, I understand the rules of volleyball much better!",
    ),
    (
        "Digital vs. Traditional Animation",
        "In the past, artists drew every frame of an anime by hand on paper. This traditional style is very beautiful, but it takes a long time. Today, most studios use digital tools and computers to make the animation faster. Some series also use 3D models, CGI, for complex movements or big monsters. Sometimes the 3D animation looks a bit strange, but it is getting better every year. I think a mix of both styles is the best for a modern anime. No matter the technology, the most important thing is the story and the heart of the characters.",
    ),
]


ANIME_TEXTS["a2"] = [
    (
        "My First Experience with Anime",
        "I remember the first time I watched an anime movie. I was only ten years old, and my older brother showed me Spirited Away. At first, I thought it was just a regular cartoon, but the story was much deeper and more mysterious than the Western animations I saw before. The characters were more complex, and the world was more magical than anything I imagined. I felt a bit scared during some scenes, but I couldn't stop watching. After that day, I started looking for more Japanese animations online. Compared to my old hobbies, watching anime became my favorite way to spend my free time. It was the beginning of my journey as a fan, and I still think that first movie was better than many modern films I watch today.",
    ),
    (
        "The Evolution of Animation Styles",
        "If you compare an anime from the 1980s with a series from 2024, the differences are incredible. In the past, the colors were softer and the lines were often thicker because everything was hand-drawn on cells. Series like Akira had a very detailed and gritty look that felt more realistic and heavy. Modern anime, however, is much brighter and the movements are often smoother because of digital tools. Some fans think that old animation was more artistic than digital animation, while others prefer the clean look of new shows. In my opinion, modern studios like MAPPA are faster at producing episodes, but some classic movies from Studio Ghibli are still more beautiful than modern CGI series. Both styles have their own charm, but technology definitely made the process more efficient.",
    ),
    (
        "A Visit to an Anime Convention",
        "Last year, I went to my first anime convention in Brasilia. It was much larger and noisier than I expected! When I entered the building, I saw hundreds of people in amazing cosplays. Some costumes were more creative than the official outfits in the shows! I bought a few posters and a small figure of a ninja for my desk. I also attended a panel where a voice actor talked about his work. He was much funnier in person than I thought. Compared to watching anime alone at home, the convention was a much more social and exciting experience. I met other students who also study software engineering and love the same series as me. It was the best weekend of my year, and I want to go again next time.",
    ),
    (
        "Comparing Subtitles and Dubbing",
        "When I started watching anime, I preferred the dubbed versions because it was easier to follow the story without reading. However, last year, I decided to switch to subtitles with the original Japanese audio. At first, it was more difficult because the characters spoke very fast, but now I think the original voices are more emotional and authentic. The Japanese voice actors, called Seiyuu, are often more talented than the actors in the dubbed versions. On the other hand, dubbing is still better when I am tired or when I am doing other things while watching. For me, subtitles are better for serious dramas, but dubbing is more convenient for long action series. It is an interesting debate among fans, but I usually choose the original audio now.",
    ),
    (
        "The Legend of the 90s Classics",
        "The 1990s were a golden era for anime. Series like Cowboy Bebop and Evangelion changed the industry forever. Last month, I decided to watch Evangelion for the first time. I thought it was just a show about giant robots, but the story was much darker and more psychological than I expected. The characters felt more broken and human than the heroes in modern Shonen anime. Compared to the shows I usually watch, the 90s classics have a unique atmosphere that feels more mature. My father told me that he watched these shows when he was younger, and we had a long conversation about the ending. It is amazing how a series from thirty years ago is still more relevant than many new releases.",
    ),
    (
        "Learning Culture Through Food in Anime",
        "One thing I noticed while watching anime is how much they show Japanese food. In the past, I didn't know what ramen or onigiri were, but after watching Naruto and Demon Slayer, I became very curious. Last weekend, I went to a Japanese restaurant to try real ramen. It was much tastier and spicier than the instant noodles I eat at home! The bowl was larger than I thought, and the ingredients were fresher. I also learned that in Japan, people make a sound when they eat noodles to show that the food is delicious. This cultural detail was more interesting than I expected. Now, I always feel hungry when I see the characters eating on screen!",
    ),
    (
        "A Sad Ending to a Great Story",
        "Last night, I finished watching a very famous tear-jerker anime called Your Lie in April. I knew the ending was sad because my friends told me, but I cried more than I planned! The story of the young pianist was more moving than any drama movie I saw recently. The music was more beautiful and more important to the plot than in other series. Compared to action-packed shows, this Slice of Life anime felt more personal and poetic. I stayed awake until 2 a.m. thinking about the characters. Even though the ending was heartbreaking, it was one of the best stories I ever experienced. Sometimes, a sad ending is more powerful than a happy one because it stays in your heart longer.",
    ),
    (
        "From Manga to the Big Screen",
        "I usually read the manga before I watch the anime adaptation. Last semester, I read a manga about a group of pirates, and I thought the drawings were incredible. When the anime version came out, I was a bit disappointed because the animation was slower than I imagined. However, the music and the voices made the battle scenes more epic than the manga. I realized that both versions have their advantages. The manga is more detailed and the pacing is faster, but the anime is more immersive because of the sound effects. Now, I follow both versions of my favorite stories. It is interesting to see how the director changes the story for the television screen.",
    ),
    (
        "The Mystery of the Isekai Genre",
        "Recently, I discovered a genre called Isekai, where a normal person travels to a fantasy world. I watched three different Isekai series last month. In the first one, the hero was much stronger than everyone else, which was a bit boring. But in the second one, the character was weaker and had to use his intelligence to survive. I found the second story more creative and exciting than the first. The fantasy worlds in these shows are often more colorful and dangerous than our real world. Although there are many Isekai shows today, some are much better written than others. It is a very popular trend right now because everyone likes the idea of starting a new life in a magic land.",
    ),
    (
        "My Favorite Antagonists",
        "In the past, I thought that every villain in anime was just a bad person who wanted to destroy the world. But recently, I watched some series where the antagonists were more complex and interesting than the heroes. For example, in Death Note, the boundary between good and evil was much blurrier than in other shows. The antagonist's motivations were more logical than I expected, and I almost agreed with him sometimes! I realized that a great story needs a villain who is more than just a monster. Comparing modern anime with older cartoons, the writing for bad guys is definitely more sophisticated now. It makes the conflict more intense and the plot more unpredictable.",
    ),
]


ANIME_TEXTS["b1"] = [
    (
        "The Global Domination of Japanese Animation",
        "The global popularity of anime has increased significantly over the last decade, transforming from a niche hobby into a mainstream cultural phenomenon. One of the primary causes for this expansion is the accessibility provided by streaming platforms. In the past, fans had to wait months for translated versions, but today, episodes are often released simultaneously worldwide. Consequently, the spoiler culture on social media has created a constant global conversation, which further drives the popularity of new series. Furthermore, anime offers a variety of genres that appeal to all age groups, unlike Western cartoons which are often perceived as being only for children. In my opinion, this diversity is the secret to its success. Because anime discusses complex themes like philosophy, grief, and politics, it resonates with adult audiences on a deeper level. Therefore, anime is no longer just a Japanese product; it is a global medium that influences fashion, music, and even Hollywood cinema.",
    ),
    (
        "The Impact of Streaming on the Anime Industry",
        "Streaming services like Netflix and Crunchyroll have permanently altered the business model of the anime industry. Because these companies invest millions of dollars in original content, production studios now have larger budgets to experiment with high-quality animation and experimental stories. Consequently, we are seeing more visually stunning series than ever before. However, this shift also has negative consequences. Due to the high demand for new content, many animators are forced to work long hours for relatively low pay. Furthermore, the industry is becoming more focused on global appeal, which some critics argue might dilute the unique Japanese cultural elements of the stories. In my view, while the investment is positive for the medium's growth, the industry must prioritize the well-being of the creators. If the workers are exhausted, the quality of the art will eventually suffer. Therefore, a balance between commercial success and fair labor practices is essential for a sustainable future.",
    ),
    (
        "Why Slice of Life is a Powerful Genre",
        "The Slice of Life genre is often criticized by casual viewers for its lack of action or supernatural elements. However, for many fans, the beauty of these stories lies in their simplicity and emotional honesty. Because these anime focus on everyday activities-like cooking, studying for exams, or talking with friends-they create a profound sense of iyashikei, or healing. Consequently, watching these shows can be a form of therapy for people living stressful lives. Furthermore, the genre often highlights the importance of small moments and personal growth. In my opinion, Slice of Life is one of the most difficult genres to write because it requires a high level of empathy and attention to detail. Instead of relying on big battles, the creators must find the extraordinary within the ordinary. Therefore, even though there are no dragons or magic, these stories can be just as epic and moving as any Shonen adventure.",
    ),
    (
        "The Rise of the Isekai Genre and Escapism",
        "The Isekai genre, where a protagonist is transported to a fantasy world, has dominated the anime market recently. This phenomenon is largely driven by the concept of escapism. Because modern life can be overwhelming and competitive, many viewers identify with the idea of starting over in a world where they have special powers or a clear purpose. Consequently, Isekai provides a perfect mental break from reality. Furthermore, the RPG mechanics often used in these stories are very familiar to the younger generation of gamers. However, some critics argue that the genre has become repetitive because many shows use the same tropes and predictable plots. In my view, while some Isekai are indeed generic, the best ones use the fantasy setting to explore deep psychological themes. Therefore, the popularity of the genre is a reflection of our collective desire for a fresh start in a simpler, more magical world.",
    ),
    (
        "The Ethical Debate Over AI-Generated Animation",
        "As Artificial Intelligence technology advances, some anime studios have started experimenting with AI-generated backgrounds and character designs. The main cause for this trend is the need to reduce production costs and speed up the animation process. Consequently, AI could help studios manage the massive volume of episodes they need to produce every year. Furthermore, it could allow smaller, independent creators to produce professional-looking anime with fewer resources. However, many artists are strongly against this technology because they believe it lacks the human touch and artistic intentionality of traditional drawing. In my opinion, if we replace human artists with algorithms, anime will lose its soul and its cultural value. Furthermore, there are serious concerns about copyright, as AI models are often trained on the work of human illustrators without their permission. Therefore, technology should be a tool to assist artists, not a replacement for human creativity.",
    ),
    (
        "Anime as a Tool for Cultural Diplomacy",
        "The Japanese government has long recognized anime as a vital component of its Soft Power and cultural diplomacy. By exporting animation, Japan is able to share its values, food, and traditions with millions of people who might never visit the country. Consequently, anime has created a positive image of Japan globally, encouraging tourism and the study of the Japanese language. For instance, many fans in Brazil started eating ramen or visiting temples because of their favorite shows. Furthermore, anime often promotes universal values like perseverance and teamwork. In my view, this is a very effective way to foster international friendship and understanding. Because stories are a universal language, they can bridge the gap between different cultures more effectively than politics. Therefore, anime is not just entertainment; it is a powerful diplomatic tool that brings the world closer to Japanese culture.",
    ),
    (
        "The Evolution of Female Characters in Shonen",
        "Historically, female characters in Shonen anime were often relegated to secondary roles or served only as damsels in distress. However, in recent years, there has been a significant shift toward more complex and powerful female leads. Because of changing social attitudes and the influence of a diverse global audience, creators are now developing women who are just as strong and motivated as their male counterparts. Consequently, series like Jujutsu Kaisen or Chainsaw Man feature female characters with their own goals and agency. Furthermore, these characters are often praised for being more realistic and less sexualized than in the past. In my opinion, this evolution is essential for the longevity of the genre. If anime continues to provide diverse and inspiring role models, it will attract an even larger audience. Therefore, the strong female lead is not just a trend, but a necessary improvement in modern storytelling.",
    ),
    (
        "The Nostalgia Factor and Remakes",
        "In the last few years, we have seen a wave of remakes and sequels of classic anime from the 80s and 90s, such as Fruits Basket and Bleach. The primary cause for this trend is nostalgia; the industry knows that adults who grew up with these shows are now willing to pay for high-quality versions of their childhood favorites. Consequently, these remakes often have much better animation and follow the original manga more closely than the old versions. Furthermore, it allows a new generation of fans to discover classic stories that they might have missed. In my view, while remakes are great, the industry should be careful not to rely too much on the past. If we only look backward, we might miss the opportunity to create new classics. Therefore, a healthy balance between celebrating history and innovating with new ideas is the best strategy for the industry.",
    ),
    (
        "The Difficulty of Translating Humor and Puns",
        "Translating anime is a complex task because Japanese humor often relies on linguistic puns and specific cultural references that do not exist in other languages. Consequently, translators often have to choose between a literal translation, which might not be funny, or a localization, which changes the joke to make it understandable for Western audiences. For instance, a joke about a Japanese historical figure might be changed to a joke about a famous singer in the West. Furthermore, certain honorifics and levels of politeness are almost impossible to translate perfectly. In my opinion, a good translation should try to keep the spirit of the original work while making it accessible. If the translation is too literal, the viewer might feel confused and disconnected from the story. Therefore, subtitle and dubbing writers are essential cultural bridges that help us appreciate the nuances of Japanese storytelling.",
    ),
    (
        "Anime and its Influence on Mental Health",
        "There is an interesting discussion about how anime can affect the mental health of its viewers. On the positive side, many fans find comfort and inspiration in characters who overcome incredible odds. Because these stories emphasize resilience and never giving up, they can provide emotional support to people going through difficult times. Furthermore, the anime community provides a sense of belonging to those who might feel isolated in their daily lives. On the negative side, some people argue that binge-watching or an obsession with waifus and husbandos can lead to a disconnection from reality. In my view, like any form of media, the key is moderation and critical thinking. If used correctly, anime can be a powerful source of motivation and a healthy way to escape stress. Therefore, we should celebrate the positive impact of these stories while staying mindful of our relationship with the screen.",
    ),
]


ANIME_TEXTS["b2"] = [
    (
        "The Deconstruction of the Magical Girl Genre",
        "For decades, the Magical Girl (Mahou Shoujo) genre was defined by its vibrant aesthetic, themes of friendship, and the inevitable triumph of good over evil. However, the release of Puella Magi Madoka Magica fundamentally altered this trajectory by introducing a subversive deconstruction of these established tropes. Instead of the traditional empowering journey, the series presents the magical contract as a Faustian bargain, fraught with existential dread and psychological trauma. Consequently, the audience is forced to confront the grim reality behind the sparkling facade. This shift proved that subverting expectations can revitalize a stagnant genre, attracting a more mature demographic. In my opinion, such deconstructions are essential for the medium's evolution, as they challenge the viewer to move beyond passive consumption and engage with the moral complexities inherent in power and sacrifice.",
    ),
    (
        "The Psychological Depth of the Mecha Genre",
        "While the Mecha genre is often associated with grand battles between giant robots, its most enduring masterpieces are those that utilize the machines as metaphors for human psychology and social alienation. Neon Genesis Evangelion remains the definitive example, where the pilots' internal struggles are far more significant than the external conflict. Consequently, the mecha itself becomes an extension of the character's ego and trauma. Furthermore, the genre often explores the ethics of technological advancement and the dehumanizing nature of warfare. In my view, the robots are merely a hook used to explore the labyrinthine depths of the human psyche. If a series focuses solely on the mechanical spectacle without grounding it in emotional realism, it fails to achieve the gravitas that defined the genre's golden age.",
    ),
    (
        "The Sakuga Phenomenon and the Cult of the Animator",
        "In recent years, the term Sakuga-referring to moments of exceptionally high-quality animation-has transitioned from industry jargon to a central focus for the global fanbase. Unlike standard animation, which relies on limited movement to save time, Sakuga sequences are characterized by fluid, hand-drawn complexity. Consequently, specific animators have gained rock star status, with fans tracking their unique styles and signatures across different studios. Furthermore, the rise of social media has allowed for the frame-by-frame analysis of these sequences, fostering a deeper appreciation for the technical labor involved. In my opinion, this movement is vital for the industry's prestige, as it highlights the artistry of the individuals behind the screen. If the focus remains on the animators' craft, it might encourage studios to prioritize artistic vision over the production line mentality.",
    ),
    (
        "The Cultural Semiotics of Kawaii in Global Media",
        "The concept of Kawaii (cuteness) is a foundational pillar of Japanese visual culture that has been successfully exported through anime to every corner of the globe. However, Kawaii is more than just an aesthetic; it is a complex semiotic tool used to evoke specific emotional responses and bridge social gaps. In anime, character designs often utilize neoteny-the preservation of juvenile features-to trigger nurturing instincts in the viewer. Consequently, even characters with dark or violent backgrounds can remain sympathetic through their visual cuteness. Furthermore, this aesthetic has become a significant driver of global merchandising, from plushies to high-fashion collaborations. In my view, the Kawaii phenomenon represents a form of soft power that allows Japan to maintain a distinct and non-threatening cultural presence. It is a sophisticated marketing strategy disguised as a simple emotional appeal.",
    ),
    (
        "The Ethics of Fan Service and Market Demands",
        "Fan service-the inclusion of gratuitous content designed to titillate the audience-remains one of the most contentious aspects of the anime industry. While proponents argue that it is a harmless commercial necessity to satisfy specific market segments, critics contend that it often undermines the narrative integrity and demeans female characters. Consequently, there is an ongoing tension between the artistic goals of the creators and the financial pressures from the production committees. Furthermore, the over-reliance on fan service can prevent a series from being taken seriously by a broader international audience. In my opinion, if a story is strong enough, it does not need to rely on such tropes to maintain engagement. However, as long as the otaku market remains the primary source of revenue for many studios, these elements are unlikely to disappear entirely.",
    ),
    (
        "The Uncanny Valley and 3D CGI in Modern Production",
        "The transition from traditional 2D cel animation to 3D CGI has been met with significant resistance from purists who argue that it often falls into the Uncanny Valley-a state where the animation looks almost human but feels unsettlingly robotic. The primary cause for this shift is the need for efficiency in animating complex mechanical objects or large crowds. Consequently, many modern series utilize a cel-shaded hybrid approach to bridge the gap between both styles. Furthermore, studios like Orange have proven that 3D can be incredibly expressive if used with a distinct artistic direction. In my view, the problem is not the technology itself, but the lack of skilled directors who understand how to apply traditional principles to a digital medium. If used correctly, 3D can expand the cinematic possibilities of anime beyond the limits of hand-drawn frames.",
    ),
    (
        "The Chuunibyou Archetype and Adolescent Identity",
        "The Chuunibyou, or Second-year Middle School Syndrome, archetype describes a character who lives in a self-constructed fantasy world to escape the mundane realities of adolescence. While often used for comedic effect, this trope is a powerful reflection of the universal struggle for identity and belonging. Consequently, these stories often resonate with viewers who felt like outsiders during their own teenage years. Furthermore, the Chuunibyou behavior functions as a defense mechanism against the pressures of social conformity. In my opinion, these series are at their best when they balance the humor of the character's delusions with a genuine empathy for their vulnerability. It is a poignant reminder that the transition to adulthood often requires the painful sacrifice of one's imaginative world to satisfy the demands of reality.",
    ),
    (
        "The Ghibli-esque Aesthetic and the Ethics of Environmentalism",
        "Studio Ghibli, particularly under the direction of Hayao Miyazaki, has popularized a specific aesthetic characterized by lush, painterly landscapes and a profound reverence for nature. This Ghibli-esque style is inextricably linked to the Shinto belief in Kami, spirits inhabiting the natural world. Consequently, the films often serve as environmental parables, warning against the hubris of industrial destruction. Furthermore, the attention to Ma-the quiet intervals of stillness-allows the viewer to reflect on the beauty of the mundane. In my view, the success of Ghibli proves that environmentalism is most effective when it is communicated through wonder rather than lecture. If modern studios continue to ignore the importance of atmosphere in favor of constant action, they risk losing the meditative depth that makes the medium truly transcendent.",
    ),
    (
        "The Rise of Grimdark Fantasy and Moral Ambiguity",
        "In recent years, the anime landscape has seen a surge in grimdark fantasy, exemplified by series like Berserk or Attack on Titan. These stories are characterized by their brutal realism, high stakes, and the absence of clear moral binaries. Consequently, the hero is often forced to commit atrocious acts to ensure survival, blurring the line between protagonist and villain. This trend reflects a shift in audience preferences toward narratives that mirror the complexities and anxieties of the real world. Furthermore, the high mortality rate of characters creates a sense of tension that is rarely found in traditional battle Shonen. In my opinion, the grimdark aesthetic is a double-edged sword; while it offers a more adult experience, it can sometimes fall into nihilism for the sake of edge, losing the emotional resonance that comes from hope.",
    ),
    (
        "The Semiotics of Color and Lighting in Ufotable Productions",
        "The studio Ufotable, famous for Fate/Zero and Demon Slayer, has revolutionized the use of digital lighting and color theory in anime. By integrating 3D visual effects with 2D character designs, they create a cinematic look that was previously reserved for high-budget films. The nuance of their style lies in the compositing-the process of layering different visual elements to create a cohesive image. Consequently, the use of dramatic lighting and saturated colors serves to heighten the emotional stakes of every scene. Furthermore, this digital polish has set a new standard for the industry, forcing other studios to upgrade their technical capabilities. In my view, while some critics argue that the style is too flashy, it represents a legitimate evolution of the medium's visual language, proving that technology can enhance rather than diminish the hand-drawn feel.",
    ),
]


ANIME_TEXTS["c1"] = [
    (
        "The Ontological Fluidity of Cyberpunk: From Akira to Ghost in the Shell",
        "The cyberpunk subgenre in anime serves as a profound meditation on the blurring boundaries between biological life and technological artifice. In seminal works such as Akira, the city of Neo-Tokyo is portrayed as a sentient entity, where the physical mutations of the protagonist mirror the chaotic expansion of urban sprawl. The nuance of this aesthetic lies in its body horror, which functions as a metaphor for the anxieties of a nation navigating rapid post-war industrialization. Conversely, Ghost in the Shell shifts the focus toward the ghost-the essence of consciousness-within a cybernetic shell. Consequently, it poses the question of whether identity can exist independently of physical form. The dialogue between these films suggests that in the digital age, the self is no longer a fixed point but a fluid, networked construct. This ontological fluidity challenges the Western Cartesian dualism, proposing instead a holistic, albeit terrifying, fusion of man and machine.",
    ),
    (
        "Shintoism and the Environmental Ethics of Studio Ghibli",
        "The cinematic output of Studio Ghibli, particularly under Hayao Miyazaki, is inextricably linked to the tenets of Shintoism-the indigenous spirituality of Japan that emphasizes the presence of kami, spirits, in all natural phenomena. Unlike Western environmentalism, which often views nature as a resource to be managed, Ghibli films portray nature as a sovereign subject with its own agency and moral weight. The nuance of this representation is most evident in Princess Mononoke, where the conflict between industrial progress and the ancient forest is not framed as a simple binary of good versus evil. Instead, it is a complex tragedy where every faction has legitimate, yet irreconcilable, claims. Consequently, the resolution is not a victory but a precarious state of co-existence. By grounding ecological themes in spiritual tradition, Ghibli elevates the environmental discourse to a level of existential necessity, suggesting that the destruction of the wild is synonymous with the death of the human soul.",
    ),
    (
        "The Semiotics of Ma: The Beauty of Stillness and Negative Space",
        "A distinguishing feature of high-level Japanese animation is the mastery of Ma-the concept of negative space or the intentional interval of stillness. While Western animation often prioritizes constant, kinetic movement to maintain the audience's attention, anime directors like Yasujiro Ozu, who influenced animation, and later, Miyazaki, utilize Ma to allow the narrative to breathe. The nuance of this technique lies in its ability to evoke mono no aware-a poignant awareness of the impermanence of things. For instance, a lingering shot of a summer cloud or a quiet street serves no direct plot purpose, but it grounds the characters in a palpable reality. Consequently, these moments of emptiness are actually dense with emotional resonance, forcing the viewer to reflect on the passage of time. To appreciate Ma is to recognize that in storytelling, the silence between the notes is just as vital as the melody itself.",
    ),
    (
        "Post-Modernism and the Meta-Narrative of Neon Genesis Evangelion",
        "Neon Genesis Evangelion is widely regarded as the definitive post-modern anime, primarily due to its deconstruction of the Mecha genre and its relentless subversion of the Hero's Journey. Throughout the series, the traditional tropes of teenage pilots saving the world are replaced by a harrowing exploration of psychological trauma, religious symbolism, and social withdrawal. The nuance of its meta-narrative lies in the final episodes, which break the fourth wall to address the audience's relationship with escapism and the medium itself. Consequently, the series ceases to be a story about giant robots and becomes a clinical analysis of the otaku psyche. This shift was controversial, yet it proved that anime could function as a high-art medium for self-reflexive critique. By confronting the viewer with their own desire for fantasy, Evangelion demands an engagement with reality that is both painful and necessary.",
    ),
    (
        "The Politics of Nostalgia: Satoshi Kon and the Fragility of Memory",
        "The works of Satoshi Kon, most notably Millennium Actress and Paprika, explore the porous boundary between reality, memory, and the cinematic image. Kon utilizes the medium of animation to visually represent the subjective experience of time, where a character might walk through a door in the present and emerge into a memory of forty years ago. The nuance of this style is its critique of nostalgia as a deceptive force that can trap a person in a cycle of repetition. In Millennium Actress, the protagonist's life is told through the history of Japanese cinema, suggesting that our personal identities are often constructed from the media we consume. Consequently, the film serves as both a celebration of art and a warning about the fragility of the self. Kon's legacy is his ability to depict the internal landscape of the mind with a level of visual sophistication that remains unmatched, proving that animation is the ultimate tool for exploring the non-linear nature of human experience.",
    ),
    (
        "The Evolution of Moe: From Aesthetic to Socio-Economic Phenomenon",
        "The concept of Moe-the intense feeling of affection for a fictional character-has evolved from a niche subcultural aesthetic into a dominant socio-economic driver within the global anime industry. However, a C1-level analysis must move beyond the surface-level cuteness to examine the deeper implications of this phenomenon. The nuance of Moe is its function as a form of affective labor, where consumers invest significant emotional and financial resources into the well-being of digital avatars. Consequently, this has led to the moe-fication of various industries, from advertising to public safety campaigns. Critics argue that this represents a regression into infantile fantasies, while proponents suggest it offers a safe space for emotional expression in an increasingly atomized society. Ultimately, Moe is a reflection of a post-industrial world where human connection is increasingly mediated by commodities and characters.",
    ),
    (
        "Grave of the Fireflies and the Aesthetics of the Tragic Sublime",
        "Isao Takahata's Grave of the Fireflies is often cited as one of the most powerful anti-war films ever made, yet it avoids the traditional tropes of battlefield combat to focus on the domestic consequences of conflict. The film's power lies in its use of the tragic sublime-an aesthetic experience that combines overwhelming beauty with profound sorrow. The nuance of its storytelling is the refusal to offer a redemptive ending; instead, it presents a clinical, unflinching look at the slow decay of a child's world. Consequently, the viewer is forced to confront the absolute failure of adult society to protect the innocent. By utilizing the medium of animation-often associated with innocence-to depict such visceral suffering, Takahata creates a cognitive dissonance that amplifies the emotional impact. It is a stark reminder that the most profound function of art is to bear witness to the unbearable.",
    ),
    (
        "The Salaryman and the Critique of Corporate Masculinity",
        "Anime frequently serves as a space for critiquing the rigid social structures of contemporary Japan, particularly the figure of the Salaryman-the corporate warrior dedicated to life-long labor. In series like Aggretsuko or The Tatami Galaxy, the absurdity and monotony of corporate life are explored through surrealism and satire. The nuance of this critique is the depiction of the lost identity that occurs when an individual's self-worth is entirely tied to their professional utility. Consequently, these stories resonate with a global audience navigating the gig economy and the collapse of traditional career paths. By utilizing hyperbole and caricature, anime exposes the hollow core of the modern work ethic, suggesting that true fulfillment lies in the chaotic, non-productive moments of human connection. The Salaryman in anime is often a tragic figure, a warning against the dehumanizing nature of late-stage capitalism.",
    ),
    (
        "Gender Performativity and Subversion in Revolutionary Girl Utena",
        "Revolutionary Girl Utena is a landmark series that utilizes the Magical Girl and Prince archetypes to conduct a sophisticated analysis of gender performativity. Influenced by the Takarazuka Revue and feminist theory, the series depicts a world where gender roles are not innate but are performed through costumes and duels. The nuance of its subversion is the protagonist's desire to become a prince rather than marry one, which disrupts the traditional patriarchal narrative of the fairy tale. Consequently, the series functions as an allegory for the liberation of the self from the constraints of societal expectation. By utilizing surrealist imagery and repetitive motifs, Utena creates a dream-like atmosphere that underscores the artificiality of the world its characters inhabit. It remains a definitive text for exploring the intersection of identity, desire, and the power of the image.",
    ),
    (
        "The Global Vibe: Lo-fi Anime Aesthetics and the Internet",
        "The rise of Lo-fi Hip Hop and the accompanying aesthetic of looped anime scenes, often from 90s shows like Sailor Moon, represents a unique moment of digital cultural convergence. This vibe is characterized by a sense of digital nostalgia for a time and place that many listeners never actually experienced. The nuance of this phenomenon is that the anime image has been detached from its original narrative context to serve as a mood-setting backdrop for modern life. Consequently, the anime girl studying has become a global icon of productivity and solitude. This highlights the capacity of the anime aesthetic to transcend its original medium and become a visual language for the internet age. It is a form of cultural remixing that proves the enduring power of the hand-drawn image in an increasingly digital and ephemeral world.",
    ),
]


ANIME_TEXTS["c2"] = [
    (
        "The Metaphysics of the Hand-Drawn Line",
        "In the digital age, where algorithmic precision threatens to sanitize the creative impulse, the hand-drawn line in Japanese animation stands as a defiant bastion of human subjectivity. This is not merely an aesthetic preference but an ontological commitment to the error as a signifier of life. When an animator like Yoshinori Kanada or Mitsuo Iso breaks the anatomical rigidity of a character to favor kinetic expression, they are engaging in a form of visual alchemy. The nuance of this practice lies in the realization that the line is not a boundary, but a trajectory of energy. In traditional cel animation, the slight inconsistencies between frames create a shimmer that mirrors the biological pulse of the viewer. To contemplate the hand-drawn line is to recognize the labor of the soul embedded in the celluloid-a testament to the fact that true art resides in the irreducible friction between the artist's hand and the medium.",
    ),
    (
        "The Phenomenological Gaze: Anime and the Construction of Subjective Reality",
        "The unique visual language of anime-characterized by its variable frame rates and dramatic shifts in perspective-offers a profound exploration of the phenomenological gaze. Unlike the objective, God's eye view of much Western cinema, anime frequently adopts a radical subjectivity, where the environment is distorted to reflect the character's internal state. The nuance of this construction is found in the spatial elasticity of action sequences, where time and distance are manipulated to prioritize emotional impact over physical accuracy. Consequently, the viewer does not merely observe the story; they inhabit the character's sensory world. This affective immersion suggests that reality is not an external fact to be recorded, but a subjective experience to be composed. In the world of animation, the real is a product of the felt, proving that the most accurate representation of life is often found in its most abstract manifestations.",
    ),
    (
        "The Dialectics of Memory and Technology in Satoshi Kon's Cinema",
        "The cinematic oeuvre of Satoshi Kon functions as a rigorous dialectical inquiry into the collapse of the boundary between the virtual and the visceral. Through his masterful use of match cuts and non-linear transitions, Kon suggests that our identities are increasingly fragmented by the media landscapes we navigate. The nuance of this critique is most evident in Paprika, where the dream world and the internet become indistinguishable, reflecting a society where collective fantasies have overwritten personal memory. This technological hauntology implies that we are living in a state of permanent simulation, where the image is more real than the object it represents. Kon's work demands that we interrogate the architecture of the self in a world where our most intimate desires are mediated by algorithms. To engage with Kon is to confront the terrifying possibility that we are merely characters in a script written by our own technological dependencies.",
    ),
    (
        "The Sublime of the Void: Tenshi no Tamago and the Theology of Despair",
        "Mamoru Oshii's Tenshi no Tamago, Angel's Egg, remains one of the most enigmatic and spiritually taxing works in the history of the medium. It is a visual poem that eschews traditional narrative in favor of a profound theology of despair. Set in a post-apocalyptic cityscape that feels like a forgotten memory of God, the film explores the weight of unending faith in a world that offers no confirmation. The nuance of its symbolism-the egg, the shadows of the fish, the water-refuses any singular interpretation, functioning instead as a Rorschach test for the viewer's own existential anxieties. This aesthetics of the void suggests that the most profound spiritual experiences are found in the absence of the divine. The film's glacial pacing and oppressive silence create a contemplative vacuum, forcing the audience to confront the terrifying silence of the cosmos. It is a masterpiece of negative theology, where meaning is found only in the persistent, albeit futile, act of hoping.",
    ),
    (
        "The Isekai Paradox: Existential Displacement and the Loss of Home",
        "While the contemporary Isekai genre is often dismissed as escapist power fantasy, a C2-level deconstruction reveals a deeper, more melancholic undercurrent of existential displacement. The act of being transported to another world is a metaphor for the profound alienation experienced by the individual in late-stage capitalist society. The nuance of this paradox is that the protagonist's power in the fantasy realm is a compensation for their powerlessness in the real world. However, this transition necessitates the absolute erasure of their previous history-a form of social death. Consequently, the Isekai hero is a ghost haunting a new reality, seeking a sense of home that is permanently deferred. This genre reflects a collective longing for a meaningful world that our current reality can no longer provide. The fantasy is not an escape from life, but an indictment of a world that has become uninhabitable for the soul.",
    ),
    (
        "The Semiotics of the Post-Human in Ghost in the Shell",
        "The 1995 film Ghost in the Shell remains the definitive cinematic inquiry into the biopolitics of the post-human condition. By situating consciousness, the ghost, within a fully modular, cybernetic body, the shell, the film deconstructs the traditional humanist notion of a stable, unified self. The nuance of this inquiry lies in the character of Major Motoko Kusanagi, whose melancholy of the machine stems from her inability to distinguish her original memories from her programmed data. This ontological instability suggests that in a networked world, the boundaries of the individual are porous and subject to constant reconfiguration. The film's conclusion-a fusion of the Major with an artificial intelligence-is not a loss of humanity, but an evolution into a distributed consciousness. It proposes a new form of existence that is post-gender, post-individual, and ultimately, post-biological. To understand Ghost in the Shell is to recognize that we have already begun the transition into the machine.",
    ),
    (
        "Masaaki Yuasa and the Liberation of the Pictorial Image",
        "The work of Masaaki Yuasa, specifically in The Tatami Galaxy and Mind Game, represents a radical liberation of the animated image from the constraints of correctness. Yuasa's style is characterized by a fluid, almost chaotic expressivism that prioritizes the feeling of the movement over the form of the object. The nuance of this approach is its rejection of the cinematic in favor of the pictorial. By allowing the characters to stretch, melt, and transform according to their emotional state, Yuasa restores the anarchic potential of animation. This formal plasticity functions as a critique of social conformity; in a world that demands rigid roles, Yuasa's characters are eternally in flux. His work is a celebration of the unbound imagination, proving that the true power of animation lies in its ability to defy the laws of physics to tell the truth about the heart.",
    ),
    (
        "The Nostalgia of the Future: Cowboy Bebop and the Aesthetics of the Outdated",
        "Shinichiro Watanabe's Cowboy Bebop is a masterpiece of retro-futurism, where the colonization of the solar system is depicted not as a gleaming utopia, but as a gritty extension of the late 20th century. The nuance of its aesthetic is the poetry of the outdated-the use of VHS tapes, analog technology, and jazz in a world of space travel. This creates a state of temporal dissonance, where the characters are physically in the future but emotionally trapped in the past. Consequently, the show functions as an elegy for a sense of cool that has already vanished. The Bebop itself is a floating ruin, a sanctuary for those who have been discarded by the march of progress. This nostalgia is not for a specific time, but for a sense of narrative weight in a world that has become increasingly ephemeral. It is the definitive work of cosmic loneliness, where the vastness of space mirrors the emptiness of the human soul.",
    ),
    (
        "The Ethics of the Cute: Moe as a Defense Against History",
        "A sophisticated analysis of the Moe phenomenon must move beyond the surface-level attraction to examine its function as a psychological defense mechanism. In the face of Japan's stagnant economy and demographic crisis, the hyper-cute aesthetic of many modern series serves as a sanctuary from the pressures of adult responsibility and historical trauma. The nuance of this infantilization is its role as a form of cultural regression-a collective desire to return to a state of pre-linguistic innocence. Consequently, the Moe character is a sacred vessel of purity that must be protected from the corruption of the real world. This reflects a profound fear of history; by focusing on the static, eternal now of the cute character, the viewer can temporarily escape the entropic reality of a nation in decline. To understand Moe is to understand the tragedy of a society that has lost faith in its future.",
    ),
    (
        "The Alchemical Cinema of Isao Takahata",
        "While Hayao Miyazaki is the fantasist, Isao Takahata was the alchemist of Studio Ghibli, a director whose commitment to experimental realism pushed the boundaries of the medium. In films like The Tale of the Princess Kaguya, Takahata utilized a sketchbook aesthetic-visible charcoal lines and watercolor washes-to highlight the act of creation itself. The nuance of this style is its refusal to provide a finished world, forcing the viewer to complete the image with their own imagination. Consequently, the film becomes a collaboration between the artist and the audience. Takahata's realism was not about documenting the surface of things, but about capturing the essence of a moment-the weight of a child's step or the sudden violence of a storm. His work is a reminder that animation is not a lesser form of cinema, but a more profound one, capable of transmuting the mundane into the transcendental through the sheer power of the observant eye.",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, vocabulario visual e estruturas de preferencia",
    "a1": "generos, termos tecnicos basicos, conectores de sequencia e presente",
    "a2": "passado simples, comparativos e descricoes de evolucao tecnica",
    "b1": "opinioes, argumentacao, causa e consequencia, conectores variados",
    "b2": "analise de tropas, desconstrucao e vocabulario academico-tecnico",
    "c1": "nuance, estilo, critica sociologica e inferencia avancada",
    "c2": "erudicao, transcendencia, registros literarios e densidade fenomenologica",
}


class Command(BaseCommand):
    help = "Replace the Anime catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="anime")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = ANIME_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-anime-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Anime texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre anime: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D cartoon style, clean lines, high quality, "
            f"educational anime culture scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
