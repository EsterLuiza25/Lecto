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
        "The Big Movie Star",
        """Tom Cruise is a very famous actor. He is in many action movies. He is brave and he does his own stunts. People all over the world know his face. He travels to many countries for movie premieres. I like his movies because they are very exciting. A movie star's life is very busy and fast. He is a pop culture icon.""",
    ),
    (
        "A Popular Singer",
        """Taylor Swift is a very popular singer and songwriter. She has many fans called Swifties. Her songs are about her life and her feelings. She plays the guitar and the piano on stage. Her concerts are very big and colorful. Many people listen to her music on their phones. Taylor is very influential in music and fashion today.""",
    ),
    (
        "What is a Meme?",
        """A meme is a funny picture or video on the internet. People share memes with their friends on social media. Usually, a meme has a small text. It can be a cat, a famous person, or a movie scene. Memes are a big part of pop culture because they make people laugh. I see many memes every day on my phone.""",
    ),
    (
        "The Red Carpet",
        """The red carpet is a special place at award shows. Famous actors and singers walk on the red carpet. They wear beautiful dresses and expensive suits. Photographers take many pictures of the celebrities. People at home watch the red carpet to see the fashion. It is a very glamorous and exciting moment in Hollywood. Everyone wants to look perfect.""",
    ),
    (
        "Superheroes are Everywhere",
        """Superheroes like Spider-Man and Wonder Woman are very popular today. We see them in movies, comics, and on T-shirts. They have special powers and they help people. Children and adults love these characters. In pop culture, superheroes represent courage and justice. Every year, there is a new movie about a hero. I have a favorite superhero poster in my room.""",
    ),
    (
        "Reality TV Shows",
        """Reality TV is a type of show about real people. Sometimes the people live in a big house or travel to an island. We watch their daily lives and their problems. Some shows are about cooking or singing competitions. Reality TV is very popular because it is dramatic and fun. Many people talk about these shows at work or at school.""",
    ),
    (
        "Social Media Influencers",
        """An influencer is a person with many followers on Instagram or TikTok. They talk about fashion, games, or food. They make videos and take beautiful photos. Companies pay influencers to show new products. Many young people want to be influencers too. They influence what people buy and what they wear. It is a new part of modern culture.""",
    ),
    (
        "Music Festivals",
        """Music festivals are big events in the summer. Many bands and singers play music for three days. People sleep in tents and wear fun clothes. Coachella is a very famous festival in the United States. Festivals are important for pop culture because they start new trends. I want to go to a music festival with my friends one day.""",
    ),
    (
        "Fashion Trends",
        """Fashion changes every year. Sometimes, people like old clothes from the 90s. Other times, they like very modern and futuristic styles. Pop stars often start new fashion trends. If a famous singer wears a green hat, many fans buy a green hat too. Fashion is a way to express who you are. I like to follow fashion news online.""",
    ),
    (
        "Going to the Cinema",
        """The cinema is a great place to watch new movies. I go to the cinema on weekends. I buy a large popcorn and a soda. The screen is very big and the sound is loud. Watching a blockbuster movie with a crowd is very exciting. Pop culture starts at the cinema. After the movie, I talk about the story with my friends.""",
    ),
]


STORY_TEXTS["a1"] = [
    (
        "The Next Big Concert",
        """My favorite band is going to perform in Brasilia next month. I am very excited because I always listen to their songs when I am studying Python. I am going to buy the tickets online tomorrow morning. Usually, tickets for famous bands sell out very fast, so I need to be quick! My friend Geovanna is going to come with me. We are going to wear matching T-shirts with the band's logo. After the show, we are going to try to take a photo with the lead singer. It is going to be the best night of the year!""",
    ),
    (
        "A New Movie Trailer",
        """Did you see the new Marvel trailer? It looks amazing! The movie is going to be in theaters in December. I usually watch every superhero movie because the special effects are great. In this new story, the hero is going to travel to a different dimension to save his friends. I am going to read the comic books this week to understand the plot better. My brother and I are going to buy popcorn and soda for the premiere. We never miss a Marvel movie on the big screen!""",
    ),
    (
        "Following an Influencer",
        """I follow a very famous tech influencer on Instagram. He always posts videos about new gadgets and software engineering tips. Next week, he is going to visit a big technology fair in California. He is going to show all the new AI tools and robots. I usually check his stories every day before I start my internship. His tips are very useful for my career. I am going to send him a question about Django during his next live stream. I think digital influencers are very important for learning new things today.""",
    ),
    (
        "The Viral Dance Challenge",
        """There is a new dance challenge on TikTok and everyone is doing it! The music is very catchy and the steps are simple but fun. My cousins are going to record a video for the challenge tonight. They usually practice the moves for two hours. I am not a good dancer, so I am just going to watch and help with the lights. They are going to use a special filter to make the video look professional. If the video goes viral, they are going to be very famous at school!""",
    ),
    (
        "Collecting Funko Pops",
        """I have a small collection of Funko Pop figures on my desk. I have characters from Star Wars, Harry Potter, and Stranger Things. I usually buy a new one every month when I receive my internship payment. Next Saturday, I am going to go to a geek store to find a rare Spider-Man figure. My collection is going to look great with a new hero! I always keep them in their original boxes to protect them. Collecting things from pop culture is a very popular hobby among my university friends.""",
    ),
    (
        "Watching a Reality Show Finale",
        """The finale of my favorite reality show is going to be on TV tonight. It is a cooking competition and the last two contestants are very talented. I usually watch the show with my family and we always talk about the recipes. Tonight, we are going to order pizza and watch the winner receive the prize. I think the young chef from Italy is going to win because his pasta is perfect. We are going to use Twitter to vote for our favorite person. It is going to be a very tense and exciting night!""",
    ),
    (
        "Trends from the 2000s",
        """Fashion from the year 2000 is becoming very popular again. Young people are wearing baggy jeans, colorful clips, and shiny jackets. I usually see these trends on Pinterest and TikTok. Next month, I am going to buy some vintage clothes at a thrift store. I want to try a new style for the next university party. My mother says she has some old bags from that time in the closet. I am going to check them tomorrow. Pop culture always brings old trends back to life!""",
    ),
    (
        "Reading a Bestseller",
        """Everyone is talking about a new fantasy book called The Golden Dragon. It is a bestseller in many countries. The story is about a girl who discovers she has magic powers. I am going to start reading it tonight before I go to sleep. Usually, I read for thirty minutes every night. This book is going to be a big movie next year, so I want to read the story first. I am also going to join an online book club to discuss the ending with other fans.""",
    ),
    (
        "A K-pop Fan's Routine",
        """My sister is a huge fan of K-pop music. She always listens to BTS and Blackpink in her room. She is learning Korean because she wants to understand the lyrics. Next summer, she is going to attend a K-pop festival in Sao Paulo. She is going to save money for six months to pay for the trip. She often watches dance covers and practices the choreography. K-pop is a global phenomenon and it is a big part of pop culture for many teenagers today.""",
    ),
    (
        "Gaming News",
        """The new PlayStation game is going to be released next Friday. I usually read gaming blogs to see the reviews. The graphics in this game are going to be more realistic than the last version. I am going to play it with my friends during the weekend. We are going to use the online mode to play together. I don't usually spend much money on games, but this one is special. It is based on a famous sci-fi movie. I think it is going to be the game of the year!""",
    ),
]


STORY_TEXTS["a2"] = [
    (
        "The Return of Vinyl Records",
        """When my father was a teenager, he always listened to music on vinyl records. Later, CDs and digital streaming became more popular because they were more convenient and cheaper. However, recently, vinyl has become trendy again among young people. Last weekend, I bought my first record player and a classic album by Queen. The sound of the vinyl is warmer and more authentic than the music on my phone. My father says that holding a large album cover is a better experience than just clicking a button. Even though streaming is the fastest way to listen to music, collecting records is more satisfying for many fans today. I think that sometimes, old technology is more charming than modern inventions. I've already started a small collection in my bedroom.""",
    ),
    (
        "A Legendary Movie Marathon",
        """Last Friday night, my friends and I had a movie marathon. We decided to watch the original Star Wars trilogy. I saw these movies when I was a child, but they were more exciting this time because I understood the story better. We stayed awake until 3 a.m., eating popcorn and talking about the characters. Compared to modern sci-fi movies, the old Star Wars films have a more nostalgic atmosphere. The special effects are older, but the story is more epic than many new blockbusters. My friend Pedro thinks that Darth Vader is the most iconic villain in history. I agree with him! After the marathon, we were very tired, but it was the most fun night of the month.""",
    ),
    (
        "The Evolution of Boy Bands",
        """Boy bands have been a part of pop culture for many decades. In the 90s, groups like the Backstreet Boys were the most famous in the world. They had millions of fans and their music videos were everywhere. Today, K-pop groups like BTS are even more successful globally. Last year, I watched a documentary about the history of pop music. I learned that modern groups practice much harder than the bands from the 90s. Their choreography is more complex and their fashion is more experimental. While the music style has changed, the passion of the fans is still the same. I think that BTS is the most influential group of this generation because they use social media better than any other artist before them.""",
    ),
    (
        "My First Comic-Con Experience",
        """Two years ago, I attended my first Comic-Con. It was the largest and most crowded event I ever visited. I saw many people dressed as their favorite characters from anime, games, and movies. I spent more money than I planned on rare comic books and t-shirts! While I was walking through the halls, I saw a famous actor from a Netflix series. He was kinder and more polite than I expected. He took photos with many fans and signed my poster. Compared to a regular party, Comic-Con is a much more immersive experience for geeks. It was the most incredible weekend of my life, and I've already started preparing my cosplay for the next event.""",
    ),
    (
        "Comparing Streaming Platforms",
        """In the past, we had to wait for movies to play on TV or rent them at a store. Now, we have many streaming platforms like Netflix, Disney+, and HBO Max. Last month, I decided to compare them to see which one is better. Netflix has the largest library of original series, but Disney+ is better for people who love superheroes and cartoons. HBO Max, however, has more serious and high-quality dramas. In my opinion, Netflix is more user-friendly, but Disney+ is more nostalgic. I've used all of them, and I think that having so many choices is better than having only a few TV channels. However, it is also more expensive! I decided to keep only two subscriptions to save money.""",
    ),
    (
        "The Rise of Female Pop Icons",
        """Last week, I read an article about the most powerful women in music today. Artists like Beyonce, Taylor Swift, and Lady Gaga are more than just singers; they are successful businesswomen. Beyonce's last tour was more spectacular than any concert I saw on TV. Her costumes were more creative and the stage was larger than a football field. I think that today, female artists have more control over their careers than in the past. In the 80s, the industry was more difficult for women. Now, they are the leaders of pop culture. My sister says that Taylor Swift is the most talented songwriter of the decade, and I think she is right. Her lyrics are more personal and poetic than most pop songs.""",
    ),
    (
        "A Nostalgic Trip to the 80s",
        """Recently, I watched Stranger Things on Netflix. The show is set in the 1980s, and it uses many elements from that decade. I saw old computers, colorful clothes, and heard classic rock music. My mother told me that her life was very similar to the show when she was a girl. She said that children were more independent because they didn't have cell phones. Compared to my life today, the 80s looked more adventurous and simpler. The music was louder and the hair was definitely bigger! After watching the series, I started listening to 80s songs on Spotify. I think that the 80s was the most creative decade for pop culture.""",
    ),
    (
        "The Best Video Game Adaptation",
        """For a long time, movies based on video games were usually bad. They were less interesting than the original games. However, last year I watched The Last of Us series, and it was incredible. The story was more emotional and the acting was better than in most action movies. I played the game three years ago, and the series was very faithful to the original plot. Pedro Pascal was the most perfect choice for the main character. Compared to the Super Mario movie from the 90s, modern adaptations are much more serious and professional. I think that directors are finally understanding that gamers want good stories, not just action scenes. It is the best game adaptation I've ever seen.""",
    ),
    (
        "The Day the Internet Changed Music",
        """I remember when my brother showed me how to download music for the first time. It was many years ago, and it was much slower than today. Before the internet, people bought physical albums or waited for the radio to play their favorite songs. The internet made music more accessible to everyone, but it also changed the industry forever. Last night, I watched a video about the history of Napster and Spotify. I learned that the internet was more disruptive than any other invention in music history. Now, we can discover artists from Japan or Iceland in seconds. While the old way was more romantic, the modern way is definitely more efficient and diverse.""",
    ),
    (
        "Celebrity Culture: Then and Now",
        """In the past, celebrities were more mysterious because there was no social media. We only saw them in magazines or on TV. Today, influencers and actors are more connected to their fans. They post photos of their breakfast and their pets every day. Last month, I started following a famous chef on Instagram. I feel like I know him because he talks to his followers every morning. However, I think that celebrities in the past were more iconic because they were more distant. Modern fame is faster, but it also disappears more quickly. In my opinion, being a celebrity today is more difficult because people are watching you all the time. I prefer to be a fan than a famous person!""",
    ),
]


STORY_TEXTS["b1"] = [
    (
        "The Power and Toxicity of Fandoms",
        """In the digital age, being a fan is no longer a passive activity; it is a collective experience that takes place on platforms like X (formerly Twitter) and Reddit. While fandoms can provide a wonderful sense of community, they can also become quite toxic. One of the primary causes of this toxicity is gatekeeping, where older fans try to decide who is a real fan and who is not. Consequently, this creates an unwelcoming environment for new people. Furthermore, some fans become so obsessed with their idols that they attack anyone who offers constructive criticism. In my opinion, we should remember that celebrities are human beings, not perfect characters. If we focused more on celebrating the art and less on attacking other fans, the internet would be a much healthier place. Therefore, while fandoms are a great source of passion, we must learn to set healthy boundaries between our personal lives and our online obsessions.""",
    ),
    (
        "The Rise of Cancel Culture",
        """Cancel Culture has become one of the most controversial topics in modern pop culture. It occurs when a celebrity or influencer says or does something offensive, and the public decides to stop supporting them. Consequently, they might lose their jobs, sponsorships, and followers in a matter of hours. In my view, holding powerful people accountable for their actions is important; however, the process can often turn into a digital mob. If someone makes a mistake, should they be punished forever, or do they deserve a chance to learn and change? Furthermore, cancel culture sometimes targets people based on unverified information. Therefore, we should practice more critical thinking before participating in a global movement of hate. While social justice is necessary, we must ensure that the punishment is fair and that there is room for genuine apology and growth.""",
    ),
    (
        "How Algorithms Shape Our Taste",
        """Have you ever noticed that Spotify and Netflix always seem to know exactly what you want to watch or listen to? This is the result of complex algorithms that analyze your past behavior. While this is very convenient, it also has a significant consequence: we are living in a filter bubble. Because the algorithm only shows us things that are similar to what we already like, we are less likely to discover something truly new or different. Furthermore, this can make pop culture feel repetitive, as artists try to create content specifically to please the algorithm. In my opinion, we should make a conscious effort to look for music and movies outside of our recommendations. If we only listen to the same style of music, our world becomes smaller. Therefore, while AI is a useful tool, we should not let it dictate our entire cultural identity.""",
    ),
    (
        "The Global Impact of South Korean Culture",
        """The Hallyu or Korean Wave has transformed South Korea into a global cultural superpower. From the massive success of K-pop groups like BTS to the popularity of K-dramas and movies like Parasite, Korean culture is everywhere. One of the main causes of this success is the high quality of production and the strategic use of social media. Consequently, millions of people around the world are now learning the Korean language and visiting the country. Furthermore, Korean artists often discuss themes like mental health and social inequality, which resonates with a global audience. In my view, this is a great example of how soft power can improve a nation's image. Because stories and music are universal, they can bridge the gap between different cultures. Therefore, the success of South Korea shows that you don't need to speak English to influence the entire world.""",
    ),
    (
        "The Death of the Traditional Movie Star",
        """In the past, people went to the cinema specifically to see a movie star like Julia Roberts or Brad Pitt. Today, however, the brand is often more important than the actor. For instance, people go to see a Marvel movie because of the characters, not necessarily because of who is playing them. Consequently, it is becoming harder for new actors to become household names based on their own talent alone. Furthermore, the rise of influencers has changed our definition of fame. Nowadays, a person with ten million followers on TikTok can be more famous than a professional actor. In my opinion, this shift has made pop culture more democratic, but also more superficial. If anyone can be famous for fifteen minutes, do we still have icons that will last for decades? Therefore, the nature of celebrity is evolving into something more ephemeral and fragmented.""",
    ),
    (
        "Nostalgia as a Marketing Tool",
        """If you look at the most popular movies and shows today, many of them are remakes or sequels of things from the 80s and 90s. This is because nostalgia is an incredibly powerful marketing tool. Because adults enjoy remembering their childhood, they are more likely to spend money on things that feel familiar. Consequently, studios prefer to invest in safe projects like Stranger Things or Top Gun: Maverick rather than original stories. While it is fun to see old characters return, some critics argue that this prevents new ideas from emerging. Furthermore, it creates a cycle where pop culture is always looking backward. In my view, we should find a balance between celebrating the past and supporting new creators. If we only consume nostalgia, the future of art will become stagnant and predictable.""",
    ),
    (
        "The Ethics of True Crime Media",
        """True Crime documentaries and podcasts have become a massive trend in pop culture recently. While these stories are fascinating, they also raise serious ethical questions. Because these shows deal with real tragedies, the creators must be very careful not to exploit the victims for entertainment. Consequently, some families of victims have complained that their trauma is being turned into a binge-watchable product. Furthermore, the obsession with true crime can lead to internet detectives who harass innocent people online. In my opinion, if we watch these shows, we should do it with a sense of empathy and respect. We must remember that these are not fictional characters, but real people with real families. Therefore, while true crime can be educational, we must be critical of how the media consumes and presents human suffering.""",
    ),
    (
        "The Environmental Cost of Fast Fashion Influencers",
        """Many fashion influencers post hauls where they show dozens of new clothes from brands like Shein or Zara. While these videos are popular, they encourage a culture of disposable fashion. Because the clothes are so cheap, people buy them, wear them once, and then throw them away. Consequently, the fashion industry is now one of the primary causes of global pollution. Furthermore, the labor conditions in the factories where these clothes are made are often terrible. In my view, influencers have a responsibility to promote more sustainable habits. If they showed their followers how to style the same piece of clothing in different ways, it would have a much more positive impact. Therefore, we should stop following people who only promote excessive consumption and start supporting those who care about the planet.""",
    ),
    (
        "The Paradox of Choice on Streaming Services",
        """We have more access to content than ever before, but this has led to a phenomenon called choice paralysis. Because there are thousands of movies on our streaming services, we often spend an hour just scrolling through the menu without picking anything. Consequently, we end up feeling frustrated instead of relaxed. Furthermore, the high number of subscriptions can be a financial burden for many people. In my opinion, less is more when it comes to entertainment. If we had fewer options, we would probably appreciate each movie or show much more. Therefore, we should be more intentional about what we watch. Instead of watching everything that is trending, we should look for stories that truly interest us. Quality is always more important than quantity in our daily cultural consumption.""",
    ),
    (
        "Representation Matters: Diversity in Media",
        """In recent years, there has been a strong movement to increase diversity and representation in movies, TV shows, and games. For a long time, the heroes in pop culture were mostly white men. Today, however, we are seeing more stories about people of different races, genders, and sexual orientations. In my view, this is a necessary and positive change. Because media shapes how we see the world, it is important that everyone sees themselves reflected on the screen. Consequently, this helps to break stereotypes and build empathy between different groups of people. Furthermore, diverse teams behind the scenes bring fresh and original ideas to the industry. Therefore, representation is not just about being political; it is about telling the full story of humanity. If pop culture is for everyone, it should look like everyone.""",
    ),
]


STORY_TEXTS["b2"] = [
    (
        "The Semiotics of the Aesthetic Trend",
        """In contemporary digital discourse, the term aesthetic has been repurposed from a branch of philosophy into a ubiquitous label for curated visual identities. From Cottagecore to Cyberpunk, these internet-driven subcultures allow individuals to signal their values and tastes through a highly specific set of visual cues. The nuance of this phenomenon lies in how it commodifies identity; by adopting an aesthetic, consumers are encouraged to purchase products that align with that specific vibe. Consequently, personal identity is often reduced to a series of aesthetic choices dictated by social media algorithms. In my opinion, while these trends offer a sense of belonging, they also promote a superficial understanding of culture. If identity is merely a costume we put on for the camera, we risk losing the authentic, uncurated parts of our human experience.""",
    ),
    (
        "The Deconstruction of the Anti-Hero",
        """For decades, the Hero's Journey dominated Western storytelling, featuring morally upright protagonists who fought for clear ideals. However, the 21st century has seen the rise of the Anti-Hero-characters like Walter White or Tony Soprano, who are fundamentally flawed and often commit atrocious acts. The appeal of the anti-hero lies in their relatability; they reflect the moral ambiguities of the real world. Consequently, audiences are forced to confront their own ethical boundaries as they find themselves rooting for a villain. In my view, this shift represents a maturing of pop culture. If we only consume stories about perfect heroes, we fail to understand the complexities of the human condition. The anti-hero serves as a mirror, showing us that the line between good and evil is often blurrier than we would like to admit.""",
    ),
    (
        "The Parasocial Relationship Paradox",
        """A parasocial relationship occurs when a fan develops a one-sided sense of intimacy with a celebrity or influencer. In the age of Instagram and Twitch, where creators share personal details of their lives daily, these relationships have become more intense than ever. Fans often feel they know their idols personally, which leads to a sense of entitlement regarding their private lives. Consequently, when a celebrity makes a mistake or deviates from the fan's expectations, the backlash can be devastating. In my opinion, this is a psychological trap for both parties. The influencer is forced to maintain a perfect digital persona, while the fan ignores their real-world connections in favor of a digital phantom. If we do not maintain a clear distinction between media and reality, the cost to our collective mental health will be significant.""",
    ),
    (
        "The Monetization of Nostalgia in the IP Era",
        """In the current entertainment landscape, Intellectual Property (IP) is king. Studios are increasingly hesitant to invest in original scripts, preferring instead to reboot, remake, or expand existing franchises like Star Wars or Harry Potter. This strategy relies heavily on the monetization of nostalgia, targeting adult audiences who want to relive their childhood experiences. Consequently, the market is saturated with familiar stories, leaving little room for innovative and diverse new voices. Furthermore, this focus on universes and multiverses often prioritizes brand consistency over narrative depth. In my view, while it is comforting to return to familiar worlds, the reliance on the past is a sign of creative stagnation. If we do not support original stories today, we will have nothing to be nostalgic for in twenty years.""",
    ),
    (
        "The Meme-ification of Political Discourse",
        """Pop culture and politics have become inextricably linked through the meme-ification of serious issues. Complex political debates are often reduced to simplified, humorous images or short videos that can be easily shared. While this can make politics more accessible to younger generations, it also leads to a dangerous level of oversimplification. Consequently, nuanced arguments are discarded in favor of viral content that reinforces existing biases. Furthermore, the speed of internet culture means that a serious crisis can be turned into a joke within minutes. In my opinion, this erosion of serious discourse is a threat to democratic health. If we only communicate through memes, we lose the ability to engage in the difficult, sustained conversations that are necessary for social progress.""",
    ),
    (
        "The Death of the Mainstream and the Rise of Micro-Cultures",
        """Before the internet, pop culture was a relatively unified experience; most people watched the same TV shows and listened to the same radio hits. Today, however, the mainstream has fragmented into thousands of digital micro-cultures. Thanks to specialized algorithms, two people living in the same house can consume entirely different media. Consequently, there is no longer a shared language of pop culture that connects the entire population. While this allows for incredible diversity and the flourishing of niche interests, it also contributes to social isolation. In my view, the loss of a common cultural baseline makes it harder to build collective empathy. If we only inhabit our own digital silos, we forget how to communicate with those who do not share our specific feed.""",
    ),
    (
        "The Girlboss Aesthetic and Corporate Feminism",
        """The Girlboss archetype-a woman who achieves success within the traditional corporate hierarchy-became a defining pop culture trend in the 2010s. It was initially hailed as an empowering movement for women in the workplace. However, critics have since deconstructed the Girlboss as a form of corporate feminism that prioritizes individual wealth over systemic change. Consequently, the movement often ignored the struggles of women who were not part of the elite professional class. Furthermore, it encouraged women to adopt the same exploitative behaviors they were trying to escape. In my opinion, true empowerment cannot be achieved by simply putting a different face on the same power structures. If feminism is to be effective, it must address the collective well-being of all women rather than celebrating the success of a few.""",
    ),
    (
        "The A24 Effect: The Rise of the Elevated Genre",
        """The film studio A24 has successfully created a brand for what critics call elevated genre films-movies that use the tropes of horror or sci-fi to explore deep psychological and social themes. Unlike traditional blockbusters, these films prioritize atmosphere, ambiguity, and artistic cinematography. Consequently, they have attracted a devoted following of cinephiles who value intellectual engagement over spectacle. In my view, this trend is a positive reaction against the generic nature of modern big-budget cinema. Furthermore, it has allowed directors like Ari Aster and Greta Gerwig to achieve mainstream success without compromising their artistic vision. If audiences continue to demand more sophisticated storytelling, the industry may finally move away from its reliance on formulaic blockbuster logic.""",
    ),
    (
        "The Ethical Dilemma of Deepfake Celebrities",
        """As Deepfake and AI technology continue to advance, the ability to recreate the likeness and voice of celebrities-both living and dead-has become a reality. This has significant implications for pop culture, from resurrecting actors for new movies to creating entirely synthetic influencers. The nuance of the dilemma lies in the loss of human agency and the potential for fraud. Consequently, there are growing legal concerns regarding publicity rights and the ownership of one's own image. In my opinion, using the likeness of a deceased person for commercial gain is a form of digital grave-robbing. If we allow AI to replace human performers, we lose the very thing that makes art meaningful: the unique, lived experience of the creator. Technology should enhance human performance, not substitute it.""",
    ),
    (
        "The Psychology of Spoilers in the Streaming Era",
        """In the age of binge-watching, the spoiler has become a major source of anxiety within pop culture communities. Because episodes are often released all at once, or at different times globally, it is nearly impossible to stay safe from information on social media. Consequently, people feel pressured to watch a new series as quickly as possible to avoid having the ending ruined. This urgency changes how we consume art, shifting the focus from the journey to the final reveal. In my view, the obsession with spoilers is a symptom of a culture that values information over experience. If a story is only good because of a surprise twist, it is probably not a very good story. A truly great work of art can be enjoyed even if you know exactly what is going to happen.""",
    ),
]


STORY_TEXTS["c1"] = [
    (
        "The Commodity of Rebellion: The Corporate Co-option of Counterculture",
        """Historically, countercultural movements-from punk to hip-hop-emerged as raw, visceral reactions against the perceived stagnation of the status quo. However, in the contemporary cultural landscape, the cycle of rebellion to brand has accelerated to a dizzying degree. The nuance of this phenomenon lies in how corporate entities now anticipate subversive trends, effectively neutralizing their revolutionary potential by pre-packaging them for mass consumption. Consequently, what once stood as a defiant critique of capitalism is frequently transformed into a lifestyle aesthetic sold back to the very demographic it sought to liberate. This recuperation of dissent suggests that in a hyper-marketed society, true subversion is nearly impossible to sustain. To understand modern pop culture is to recognize that rebellion has become one of its most profitable products, a sanitized version of anger that offers the feeling of resistance without the risk of social upheaval.""",
    ),
    (
        "The Semiotics of Camp and the Aesthetic of Excess",
        """The concept of Camp, famously articulated by Susan Sontag, has undergone a radical transformation as it moved from the clandestine underground of queer subcultures into the mainstream spotlight of the Met Gala. At its core, Camp is an aesthetic of artifice, an extravagant theatricality that finds beauty in the exaggerated and the too much. The nuance of Camp lies in its inherent irony; it is a way of seeing the world as an aesthetic phenomenon, prioritizing style over content. However, as Camp becomes a curated marketing tool for luxury brands, there is a risk that its subversive, parodic edge is being blunted. When the failed serious is intentionally manufactured for viral engagement, it loses the organic sincerity that once defined it. Consequently, we must ask if Camp can survive its own popularity, or if the mainstreaming of the marginal inevitably leads to the death of the very irony that gave it life.""",
    ),
    (
        "The Myth of the Great American Novel in the Age of Peak TV",
        """For decades, the Great American Novel was considered the definitive medium for capturing the zeitgeist of a nation. Today, however, that cultural weight has largely shifted toward the serialized prestige drama. Shows like The Sopranos, The Wire, and more recently, Succession, utilize the temporal expansiveness of television to construct complex, multi-layered narratives that rival the psychological depth of classic literature. The nuance of this shift is the novelization of the screen, where the audience's relationship with characters is sustained over years rather than hours. Consequently, the cultural conversation is now dominated by the episodic, leading to a fragmented canon where the visual medium has usurped the written word as the primary vehicle for social critique. This evolution suggests that our capacity for deep, sustained narrative has not vanished, but has merely found a more accessible, albeit more commercial, home.""",
    ),
    (
        "The Hollow Icon: The Post-Human Celebrity and AI Authorship",
        """The advent of generative AI and holography is ushering in an era of the post-human celebrity, where the physical existence of the artist is becoming increasingly irrelevant to their commercial viability. From AI-generated pop stars to posthumous concert tours of deceased legends, the nuance of this technological shift is the severing of the ghost from the machine. Consequently, we are witnessing the birth of the Hollow Icon-a brand that can be infinitely iterated, updated, and monetized without the messy unpredictability of human agency. This poses a profound challenge to the traditional notion of artistic soul. If a song can be written by an algorithm and performed by a digital likeness, does the lack of lived experience diminish the emotional truth of the work? To engage with post-human pop culture is to confront the possibility that we are entering a period of synthetic nostalgia, where the past is eternally recycled by machines.""",
    ),
    (
        "The Panopticon of Social Media: Fame as a Form of Surveillance",
        """In the traditional era of Hollywood, fame was a distant, carefully managed facade. In the current Creator Economy, however, fame has become a form of voluntary, twenty-four-hour surveillance. The nuance of this modern celebrity is the burden of transparency; to remain relevant, influencers must provide their audience with a constant stream of intimate details, effectively turning their private lives into a digital performance. Consequently, the boundary between self and brand has entirely collapsed. This creates a psychological panopticon where the creator is simultaneously the prisoner and the guard, constantly monitoring their own behavior to satisfy the shifting whims of the algorithm. The authenticity that fans demand is, paradoxically, a highly engineered product. This suggests that the cost of modern fame is not the loss of privacy, but the loss of a private self that exists independent of the digital gaze.""",
    ),
    (
        "The A24-ification of Taste and the Performance of Sophistication",
        """The rise of indie studios like A24 and Neon has created a new category of cultural consumer: the elevated fan. These individuals distance themselves from the low-brow spectacle of superhero blockbusters, seeking instead the atmospheric ambiguity of prestige horror or auteur-driven dramas. The nuance of this trend is the performance of sophistication, where the consumption of certain media serves as a marker of intellectual and social status. Consequently, taste has become a form of cultural capital, used to navigate the hierarchies of digital subcultures. However, critics argue that this elevated genre is often more about style and vibe than actual narrative innovation. This suggests that the desire for alternative culture is frequently just another form of brand loyalty, where the studio's logo becomes a shorthand for a specific, curated identity.""",
    ),
    (
        "The Death of the Subculture and the Rise of the Algorithmic Niche",
        """Historically, subcultures-such as Goths, Mods, or Grime artists-were tied to specific geographic locations and slow-burning underground scenes. In the age of TikTok, however, subcultures are replaced by algorithmic niches that can emerge and vanish in a matter of weeks. The nuance of this shift is the loss of friction; because information travels instantly, a niche style is immediately exposed to the mainstream, leaving no time for the community to develop a deep, resistant identity. Consequently, we are living in a state of cultural hyper-acceleration, where trends are consumed and discarded before they can achieve any historical weight. This suggests that the underground no longer exists as a site of long-term development, but has become a mere R&D department for the mainstream fashion and music industries.""",
    ),
    (
        "The Semiotics of the Stan and the Erosion of Critical Distance",
        """The term stan-derived from Eminem's song about an obsessive fan-has shifted from a cautionary tale of madness into a celebrated identity of devotion. Modern stan culture is characterized by an absolute, often militant, loyalty to a celebrity, where any form of criticism is viewed as a personal attack. The nuance of this behavior is the identification of the self with the idol; when the celebrity succeeds, the fan feels a sense of personal triumph. Consequently, the critical distance necessary for objective analysis has been entirely eroded. This tribalism within pop culture mirrors the polarization of modern politics, where loyalty to the brand overrides the pursuit of truth or nuance. This suggests that in a fragmented world, celebrities have become the new secular deities, providing a sense of purpose and community that traditional institutions can no longer offer.""",
    ),
    (
        "The Architecture of the Spoiler and the Tyranny of the Twist",
        """In the streaming era, the spoiler has become the ultimate cultural taboo, leading to a narrative architecture that prioritizes the twist over the journey. Because audiences are terrified of having the ending revealed on social media, there is a frantic pressure to consume new content immediately upon release. The nuance of this anxiety is the reduction of art to information; a story is viewed as something to be solved rather than something to be experienced. Consequently, directors are increasingly forced to rely on shock value and mystery boxes to maintain engagement, often at the expense of character development and thematic depth. This suggests that our relationship with narrative has become transactional-we trade our time for a reveal-ignoring the fact that a truly great work of art remains profound even when the ending is known.""",
    ),
    (
        "The Gendered Politics of the Pop Girl Renaissance",
        """The current Renaissance of the female pop star-from the era-defining dominance of Taylor Swift to the hyper-conceptual work of Charli XCX-represents a sophisticated reclamation of the feminine within pop culture. For years, pop was dismissed as a frivolous, superficial genre compared to the serious masculinity of rock or hip-hop. The nuance of this shift is the intellectualization of the pop star, where these women utilize high-concept fashion, complex lyricism, and savvy business strategies to challenge patriarchal industry standards. Consequently, the Pop Girl has become a site of intense academic and social analysis, reflecting broader debates about autonomy, agency, and the performance of gender. This suggests that the mainstream is currently the most fertile ground for exploring the complexities of identity, proving that the most popular art can also be the most subversive.""",
    ),
]


STORY_TEXTS["c2"] = [
    (
        "The Apotheosis of the Image: Pop Culture as Secular Religion",
        """In the wake of the death of God articulated by Nietzsche, the vacuum of transcendence has been occupied not by a rational humanism, but by the shimmering, multifaceted pantheon of pop culture. This transition represents an apotheosis of the image, where the celebrity functions as a secular deity-a vessel for the projection of collective anxieties, desires, and moral aspirations. The nuance of this new theology lies in the ritualization of consumption; the concert, the premiere, and the viral moment serve as contemporary liturgies that provide a sense of communal belonging in an increasingly atomized world. Consequently, the distinction between the sacred and the profane has been blurred, as the star inhabits a liminal space between the human and the divine. This suggests that pop culture is not merely a form of entertainment, but a fundamental ontological framework through which the modern subject negotiates their place in the universe. To worship at the altar of the icon is to seek a form of immortality in a world of digital flux.""",
    ),
    (
        "The Hauntology of the Reboot: Nostalgia as Ontological Stagnation",
        """The contemporary obsession with reboots, remakes, and retconning is the most visible symptom of what Mark Fisher described as hauntology-the persistence of past futures that failed to materialize. In the sterile corridors of late-stage cultural production, the past is eternally recycled because the present has lost its capacity to imagine a new that is not a derivative of the familiar. The nuance of this stagnation lies in the digital preservation of the ghost; through high-definition restoration and AI-driven de-aging, we maintain the illusion that our cultural heroes are immune to the ravages of time. Consequently, we inhabit a static future, where the markers of innovation are merely technical improvements upon a fixed aesthetic canon. This suggests a collective failure of the imagination, a retreat into the safety of the known to avoid the terrifying uncertainty of a genuine cultural shift. Pop culture has become a cemetery of ideas, beautifully curated and perpetually revisited, but ultimately devoid of the vital friction of the unprecedented.""",
    ),
    (
        "The Semiotics of Brat and the Radical Reclamation of Abjection",
        """The recent emergence of Brat as a cultural signifier-exemplified by Charli XCX's conceptual hyper-pop-represents a sophisticated, C2-level reclamation of abjection and messiness as a defiant political stance. In a digital landscape dominated by the curated perfection of the Clean Girl aesthetic, Brat celebrates the erratic, the hedonistic, and the profoundly unpolished. The nuance of this movement is its intellectualization of the failure to perform; it is a deliberate embrace of the visceral reality of the feminine experience that refuses to be sanitized for corporate consumption. Consequently, it functions as a critique of the Girlboss feminism of the previous decade, prioritizing raw authenticity over institutional success. This suggests that the current cultural moment is shifting away from the aspirational toward the existential, finding a radical freedom in the refusal to be useful or palatable. To be Brat is to insist on the right to be human in a world that demands a modular, optimized performance.""",
    ),
    (
        "The Spectacle of the Self: Guy Debord in the Age of the Influencer",
        """Guy Debord's The Society of the Spectacle argued that all lived experience had been replaced by its representation. In the age of the influencer, this prophecy has achieved its terminal velocity. The self is no longer an interior reality to be nurtured, but a spectacle to be broadcast, measured, and monetized. The nuance of this condition is the commodification of the gaze; we no longer witness our lives as they happen, but as potential content for a digital audience. Consequently, the boundary between the private and the public has not only collapsed but has been entirely inverted. The influencer is the ultimate expression of the proletarianization of fame, where the labor of self-curation becomes an all-consuming task. This suggests that we have entered a period of absolute mediation, where the real only exists to provide the raw material for the image. To exist is to be seen, and to be seen is to be a product in the global market of attention.""",
    ),
    (
        "The Alchemical Cinema of David Lynch: Pop Culture as Dreamwork",
        """The cinematic oeuvre of David Lynch functions as a rigorous alchemical transmutation of American pop culture tropes-the diner, the detective, the starlet-into a surrealist landscape of the subconscious. Lynch deconstructs the facade of mid-century Americana to reveal the monstrous that lurks beneath the surface of the mundane. The nuance of his work lies in its atemporal resonance; he utilizes the language of soap operas and noir films to explore the timeless, archetypal structures of human desire and dread. Consequently, his films do not function as traditional narratives but as phenomenological events that demand a radical openness from the viewer. This suggests that the true power of pop culture lies in its capacity for mythopoesis-the ability to create new myths that resonate with the deep, non-linear logic of the dream. To watch Lynch is to recognize that the most popular symbols are often the keys to the most private terrors.""",
    ),
    (
        "The Dialectics of the Camp Aesthetic and the Death of Irony",
        """Susan Sontag's characterization of Camp as a love of the unnatural and the exaggerated has been profoundly challenged by the total irony of the internet age. When everything is meta and every cultural artifact is consumed with layers of cynical detachment, can Camp truly exist? The nuance of this dialectic is the exhaustion of the parodic; because we are so aware of the artifice of our culture, the act of subverting it through exaggeration becomes redundant. Consequently, we are witnessing a return to sincerity that is, paradoxically, mediated by the very tools of irony it seeks to escape. This suggests that the post-Camp era is one of profound confusion, where we struggle to find a stable ground for genuine emotion amidst the noise of a thousand memes. To understand modern pop culture is to navigate this hall of mirrors, where the distinction between the serious and the ironic has been permanently dissolved.""",
    ),
    (
        "The Hollow Canon: The Erosion of Cultural Memory in the Digital Library",
        """The transition from physical archives to streaming libraries-the Netflix-ization of culture-has created a Hollow Canon characterized by a profound lack of historical depth. While we have access to more information than ever, the logic of the search prioritizes the recent and the trending, effectively erasing the cultural lineage that preceded the digital era. The nuance of this erosion is the loss of context; a film from 1950 is presented alongside a TikTok compilation, stripped of the historical and social framework that gave it meaning. Consequently, the modern consumer lives in a collapsed timeline, where all art is consumed in a flat, ahistorical now. This suggests that our cultural memory is becoming increasingly ephemeral, subject to the whims of licensing agreements and algorithmic preferences. To protect the canon is to insist on the gravity of history in a world that prefers the weightlessness of the infinite scroll.""",
    ),
    (
        "The Semiotics of the Stan and the Architecture of the Digital Hive",
        """Stan culture represents a radical evolution of the fan-artist relationship, transforming the solitary act of admiration into a coordinated, military-like campaign of digital defense. The stan identifies so completely with their idol that any perceived slight against the celebrity is felt as a personal existential threat. The nuance of this behavior is its networked agency; by organizing on social media, stans can influence market trends, manipulate charts, and silence critics. Consequently, the celebrity becomes a distributed consciousness, a brand sustained by the collective labor of a global hive. This suggests a new form of digital tribalism, where identity is constructed through the aggressive defense of a cultural icon. To be a stan is to participate in a secular crusade, finding a sense of power and purpose in the absolute submission to the image of another.""",
    ),
    (
        "The Metaphysics of the Glitch: Error as a Signifier of Authenticity",
        """In a pop culture landscape characterized by the seamless, algorithmic perfection of Autotune and CGI, the glitch-the accidental error, the distorted sound, the visual artifact-has become the ultimate signifier of authenticity. This aesthetics of the broken serves as a defiant critique of the sanitized, hyper-produced reality of mainstream media. The nuance of the glitch is its reminder of the machine; it exposes the technological substrate that usually remains hidden, forcing the viewer to confront the artificiality of the spectacle. Consequently, the glitch has been co-opted by artists as a deliberate style, a way of signaling a subversive intent through the mimicry of failure. This suggests that in an age of perfect simulation, the broken is the only thing that feels real. To embrace the glitch is to find beauty in the friction between the human impulse and the digital medium.""",
    ),
    (
        "The Epistemology of the Deepfake: The End of Visual Truth",
        """The emergence of high-fidelity Deepfake technology marks the terminal point of the truth of the image in pop culture. When a digital facsimile can speak, move, and emote with indistinguishable accuracy from a living person, the photograph ceases to be a document of reality and becomes a mere suggestion of it. The nuance of this epistemological shift is the death of the witness; we can no longer trust our eyes to provide us with an accurate account of the world. Consequently, pop culture becomes a play of shadows, a realm of pure simulation where the real is a redundant category. This suggests a future where fame is entirely decoupled from the human body, and history is a plastic medium that can be reshaped at will. To navigate the era of the Deepfake is to accept a world of radical uncertainty, where the only truth is the one we choose to believe in.""",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, vocabulario de fama e entretenimento e estruturas de gosto",
    "a1": "futuro com going to, frequencia, preferencias, fandoms e midia",
    "a2": "passado simples e continuo, comparativos, superlativos e experiencias culturais",
    "b1": "opinioes, argumentacao, causa e consequencia e vocabulario de midia digital",
    "b2": "critica de midia, semiotica da fama e vocabulario academico",
    "c1": "critica cultural avancada, teoria da midia e registros formais literarios",
    "c2": "registro erudito, ensaio critico-filosofico e densidade semiotica",
}


class Command(BaseCommand):
    help = "Replace the Cultura pop catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="cultura-pop")
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
                text.slug = slugify(f"{level.slug}-cultura-pop-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Cultura pop texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre cultura pop: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D pop culture educational magazine style, clean lines, high quality, "
            f"scene about {title}, showing {scene}, featuring the book-mascot Alexandrinho, "
            "using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
