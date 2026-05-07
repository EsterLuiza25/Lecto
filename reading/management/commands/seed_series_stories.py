import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


SERIES_TEXTS = {
    "iniciante": [
        (
            "The Big TV",
            "The TV is on the wall. It is a very big TV. Leo sits on the sofa. He has a remote control. Leo press a button. A new series starts. The series is about a family. Leo is happy. He likes the big TV. The sofa is soft. Watching series is a fun activity.",
        ),
        (
            "A Funny Show",
            "This series is very funny. There are four friends. They live in a small apartment. One friend is a doctor. One friend is a teacher. They talk and laugh every day. The jokes are simple. Anna watches the show on her laptop. She smiles a lot. It is a good series for a sunny day.",
        ),
        (
            "The Hero in Green",
            "Mark is a hero in a series. He wears green clothes. Mark is very strong and fast. He helps people in the city. The city is big and dark. Every episode has a new problem. Mark solves the problem. Children like the hero in green. He is brave. The series is exciting.",
        ),
        (
            "The Mystery Box",
            "A small girl finds a mystery box. The box is in the garden. This is the first episode of the series. What is in the box? No one knows. The girl is curious. Her brother is curious, too. They open the box slowly. The series is a mystery. It is very interesting to watch.",
        ),
        (
            "Cooking with Chef Sam",
            "Chef Sam has a cooking series. He is in a large kitchen. Sam has many vegetables and eggs. He makes a delicious cake today. The series shows how to cook. It is very easy to learn. Maria watches the series every Friday. She wants to be a chef, too. Cooking is fun with Sam.",
        ),
        (
            "Space Journey",
            "This series is about space. There is a large silver ship. The ship travels to the stars. The stars are bright and far. Three astronauts live in the ship. They see new planets. One planet is red. One planet is blue. The series is beautiful. Space is a big mystery.",
        ),
        (
            "The Hospital Series",
            "The series is in a big hospital. Many doctors work there. They wear white coats. Dr. Smith is very kind. He helps the sick people. Every day is a busy day. The hospital is quiet at night. Jane watches the series on her phone. She wants to help people, too. It is a serious show.",
        ),
        (
            "Cartoon Friends",
            "This is a cartoon series. There is a blue dog and a yellow cat. They are best friends. They play in the park every day. The dog has a red ball. The cat has a small toy. The series is for children. It is very colorful. The dog and the cat are very happy together.",
        ),
        (
            "The School Bus Series",
            "Five students are on a school bus. The bus is yellow and big. This series is about school life. The students have books and pens. They go to the library. They play sports in the afternoon. The teacher is friendly. Watching the series is like being at school. It is a nice story.",
        ),
        (
            "Sunday Night Series",
            "It is Sunday night. The family is in the living room. They watch a historical series. The people wear old clothes. They have horses and large houses. The series is very long. The father likes the history. The mother likes the costumes. It is a quiet time for the family.",
        ),
    ],
    "a1": [
        (
            "Weekend Binge-Watching",
            "On Saturday afternoons, I love to watch my favorite series for many hours. This activity is called binge-watching. I sit on my comfortable sofa with a large bowl of popcorn and a cold soda. Currently, I am watching a series about a group of teenagers in a small town. The story is very exciting because every episode ends with a big surprise. I usually watch three or four episodes in a row because I want to know the end of the mystery. My sister sometimes watches with me, but she prefers romantic comedies. We have a great time together in front of the TV.",
        ),
        (
            "My Favorite Character",
            "In the series The Brave Explorer, my favorite character is a woman named Lara. She is very intelligent and she speaks five different languages. Lara travels to old ruins and finds ancient treasures. I like her because she is brave and she never gives up, even when the situation is difficult. In the latest episode, she discovered a hidden map in a dark cave. She also has a small robot friend that helps her with technology. I think Lara is a great role model for students. I always wait for the new episodes every Thursday night because her adventures are amazing.",
        ),
        (
            "Choosing a New Series",
            "There are many different platforms to watch series today, so choosing a new show is sometimes difficult. First, I read the descriptions and watch the trailers to see the genre. I like science fiction and police dramas, but I don't like horror stories because I feel scared at night. My friend Lucas always gives me good recommendations. He says that a series about a futuristic city is perfect for me. I also check the ratings online to see if other people like the show. When I find a good series, I save it to my list and watch the first episode immediately.",
        ),
        (
            "Watching Series in English",
            "I am a student and I use series to practice my English every day. Usually, I watch a comedy show because the dialogues are short and useful. First, I watch with subtitles in Portuguese to understand the story. Then, I watch the same episode again with English subtitles. This helps me learn new words and listen to the correct pronunciation. Sometimes the characters speak very fast, but I can pause the video and repeat the sentences. It is a very fun way to study because I don't feel like I am in a classroom. My English is getting better every week!",
        ),
        (
            "The History of a Famous Series",
            "One of the most famous series in the world is about six friends living in New York City. The show started many years ago, but people still watch it today. The episodes are about their daily lives, their jobs, and their funny problems. I like this series because the characters are very different and relatable. For example, one friend is a chef and another is an actor. They often meet at a small cafe to talk. My mother watched this show when she was young, and now we watch it together. It is a classic series that makes everyone laugh, no matter their age.",
        ),
        (
            "A Series About Nature",
            "This month, I am watching a documentary series about nature and wild animals. The cinematography is beautiful because they use high-quality cameras and drones. In the first episode, they show the life of lions in Africa. The narrator has a very calm voice and explains how the animals find food and protect their families. I like this show because I learn many facts about the planet. For example, I didn't know that some birds can fly for many days without stopping. It is a very educational series for the whole family, and the images of the forests are spectacular.",
        ),
        (
            "Discussing Series with Friends",
            "Every Monday at school, my friends and I talk about the series we watched during the weekend. We have a group on WhatsApp specifically for this. We discuss the plot twists and the destiny of the characters. Sometimes we have different opinions, but it is always interesting to listen to my friends. We are careful not to give spoilers to people who didn't finish the episode yet. If a series is very good, we tell everyone to watch it. Discussing the stories makes the experience much better because we can share our theories about the next season.",
        ),
        (
            "The Mystery of the Blue House",
            "The Blue House is a new mystery series on my favorite platform. The story is about a family that moves to a very old house in the mountains. Strange things happen every night, and the children hear noises in the attic. The parents don't believe them, but the viewers see the truth. The atmosphere of the show is very dark and quiet. I like the music in this series because it creates a lot of suspense. I only watch this show during the day because I am a bit nervous. It is the best mystery show I watched this year.",
        ),
        (
            "Cartoon Series for Adults",
            "Many people think that cartoons are only for children, but there are many great animated series for adults. These shows often have complex stories and social criticism. My favorite cartoon series is about a scientist and his grandson traveling to different dimensions. The humor is very intelligent and sometimes a bit strange. The animation style is colorful and creative. I like to watch an episode after work because it helps me relax and laugh. It is amazing how much imagination the creators have. Animated series can show things that are impossible in real-life shows.",
        ),
        (
            "Waiting for the New Season",
            "I finished my favorite series last night, and now I feel a bit sad. The final episode was very emotional, and many questions are still open. Now, I need to wait for one year for the new season to arrive. This is the difficult part of being a fan! I follow the actors on social media to see photos of the filming process. Sometimes, the producers release small videos to make the fans excited. While I wait, I try to find a similar series to watch. I hope the next season is as good as the first one!",
        ),
    ],
    "a2": [
        (
            "The Evolution of My Favorite Show",
            "Last year, I started watching a famous drama series about a group of doctors in Seattle. In the first season, the stories were simpler and more focused on the medical cases. However, as I moved to the second and third seasons, the plot became much more complex and emotional. I think the earlier episodes were funnier than the new ones, but the character development in the later seasons is significantly better. Last week, I watched the season finale, and it was the most shocking episode I ever saw! I cried when my favorite character decided to leave the hospital. Compared to other medical shows, this series is much more dramatic and intense. I already recommended it to my friend Geovanna because she loves stories about life and death. Now, I am waiting for the next season to start on my favorite streaming platform.",
        ),
        (
            "A Retro Series Marathon",
            "During my last vacation, I decided to watch an old sitcom from the 1990s. My parents always said that comedies from the past were better than modern shows, so I wanted to see if they were right. The series is about three families living in the same neighborhood. At first, the clothes and the technology looked very strange to me because they didn't have smartphones or social media. But after three episodes, I realized that the jokes were still very funny and relatable. Actually, I think the writing in this old show is more creative than in many series today. I finished all ten seasons in just two weeks! It was a very nostalgic experience, and it helped me understand the culture of that decade. I still prefer modern high-definition images, but the heart of this classic show is definitely bigger.",
        ),
        (
            "The Mystery of the Missing Key",
            "Last month, a new mystery series appeared on my list. The story began with a young woman who moved into a mansion that belonged to her grandmother. On her first night, she found a small silver key hidden under a loose floorboard. This series was much more suspenseful than the mystery show I watched last summer. Every episode revealed a new secret about her family's past. I tried to guess the ending, but the plot twists were always more surprising than my theories. The acting was also superior to other shows in the same genre. In the final episode, we finally discovered what the key opened, and it was a very emotional moment. I felt like a real detective while I was watching. It is definitely the most intriguing series of the year.",
        ),
        (
            "Comparing Two Superhero Shows",
            "Recently, I watched two different series about superheroes. The first one was a classic story about a man with super strength who protected a big city. It was a good show, but it was a bit predictable. The second series was much darker and more realistic. It showed the problems that superheroes face in their daily lives and how they deal with fame. In my opinion, the second show is much more interesting because the characters are more human and have many flaws. The special effects in the realistic show were also more impressive than in the classic one. My classmate Lucas preferred the first series because he likes traditional heroes, but I enjoyed the complexity of the second one. It is fascinating to see how different creators can imagine the same concept in such distinct ways.",
        ),
        (
            "A Journey Through Time",
            "I just finished a fascinating science fiction series about time travel. The main character was a scientist who accidentally traveled to the year 1920. The costumes and the sets were more beautiful than any other period drama I watched before. It was very interesting to see the contrast between the past and the modern world. In one episode, the scientist tried to explain a laptop to a person from 1920, and it was the funniest scene in the whole series! However, the story also had some sad moments because he couldn't return to his own time easily. This series was more educational than I expected because I learned a lot about history while I followed the plot. I think time travel is the most exciting theme for a series.",
        ),
        (
            "The Cooking Competition Finale",
            "Last night, I watched the final episode of a famous cooking competition series. There were three finalists, and they had to cook a three-course meal in only two hours. The atmosphere in the kitchen was more intense than in a professional restaurant! I felt very nervous for the contestants because the judges were extremely strict. One of the chefs made a mistake with the dessert, and it was a very dramatic moment. In the end, the youngest chef won the prize, and he was the happiest person in the world. I like this kind of series because it is more exciting than a regular cooking show. It also gives me many ideas for new recipes to try at home, although I am not as fast as the professionals.",
        ),
        (
            "Animated Series for Everyone",
            "Some people think that animated series are only for children, but I recently watched a cartoon that was more mature than many live-action shows. The story was about a group of animals living in a magical forest that was under threat. The animation style was more colorful and artistic than the cartoons I watched when I was younger. The series discussed important themes like friendship, loss, and the environment. I think the dialogue was more intelligent and deeper than in many popular comedies. My friend Clara watched it with me, and we both agreed that the ending was very moving. This series proved to me that animation is a powerful medium for storytelling for all ages.",
        ),
        (
            "A Series About a High School Band",
            "Last week, I started a musical series about four students who formed a rock band at their high school. At first, they were very bad at playing their instruments, and they argued a lot. But as they practiced more, they became a great team. The music in this show is better than the songs on the radio! I especially liked the episode where they played their first concert in the school gym. They were more nervous than I am before an exam! The series also showed their personal problems with their families and friends. It was a very relatable story for any student. I think the lead singer is a more talented actor than the other cast members. I can't wait to download the soundtrack of the show.",
        ),
        (
            "The Documentary Series: Planet Earth",
            "I am currently watching a documentary series about different ecosystems on our planet. The latest episode was about the deep ocean, and it was more terrifying and beautiful than a science fiction movie. They showed creatures that live in total darkness and have their own lights. The technology they used to film these animals is more advanced than anything I saw in the past. The narrator explained the importance of protecting the oceans from pollution and climate change. I feel more conscious about nature after watching this show. Documentary series are a great way to learn about the world while you are sitting on your sofa. It is definitely more informative than reading a textbook.",
        ),
        (
            "Why I Quit Watching a Popular Series",
            "Everyone at my university was talking about a new fantasy series, so I decided to watch the first few episodes. However, I didn't like it as much as my friends did. I thought the plot was more confusing than interesting, and there were too many characters to remember. The special effects were great, but the story was slower than I expected. After four episodes, I decided to stop watching. I prefer series that have a faster pace and clearer goals for the characters. My friend Geovanna said that it gets better in the second season, but I don't want to wait that long. Sometimes, a popular series is just not the right fit for your personal taste.",
        ),
    ],
    "b1": [
        (
            "The Impact of Streaming Platforms on TV Habits",
            "The rise of streaming platforms like Netflix, Disney+, and HBO Max has fundamentally transformed our television consumption habits over the last decade. In the past, viewers had to wait a full week to watch a new episode of their favorite show, which created a sense of anticipation and shared community. However, because these platforms often release entire seasons at once, the phenomenon of binge-watching has become the new standard. Consequently, many people now finish a ten-episode series in a single weekend. While this provides instant gratification, some critics argue that it reduces the long-term impact of the story because viewers don't have time to reflect on the plot between episodes. Furthermore, the massive amount of content available can lead to decision fatigue, where users spend more time scrolling through the menu than actually watching a show. In my opinion, while the convenience of streaming is undeniable, we have lost the water cooler effect-the social experience of discussing the same episode with colleagues the next morning. Therefore, finding a balance between binging and savoring a story is essential for a better viewing experience.",
        ),
        (
            "Why We Love Anti-Heroes in Modern Dramas",
            "For a long time, protagonists in television series were either perfectly good or purely evil. However, modern dramas have introduced a more complex character: the anti-hero. These characters, like Walter White in Breaking Bad or Tony Soprano, often do terrible things, yet the audience remains deeply invested in their journeys. This shift happened because viewers began to crave more realistic and nuanced storytelling. Because anti-heroes are flawed and morally ambiguous, they feel more human than traditional heroes. Consequently, we find ourselves rooting for them even when they make unethical decisions. Furthermore, these characters allow writers to explore the darker aspects of the human psyche and social structures. In my view, the popularity of the anti-hero proves that audiences are looking for intellectual challenges rather than simple moral lessons. Although it can be uncomfortable to sympathize with a villain, it makes for a much more compelling and unpredictable narrative. In conclusion, the era of the perfect hero is over, and the complex anti-hero is here to stay.",
        ),
        (
            "The Global Success of Non-English Series",
            "One of the most interesting consequences of the digital era is the global success of non-English language series. Shows like Squid Game from South Korea and Money Heist (La Casa de Papel) from Spain have reached the top of the charts in English-speaking countries. This phenomenon proves that a good story can transcend linguistic and cultural barriers. In the past, Hollywood dominated the global market, but because of high-quality dubbing and subtitling, international productions are now more accessible than ever. Consequently, audiences are becoming more open to different cultures and storytelling styles. Furthermore, this competition is forcing producers worldwide to improve their quality to compete on a global scale. In my opinion, this diversity is fantastic for the industry because it allows creators from smaller countries to find a massive audience. If we continue to support international shows, we will have a much richer and more inclusive media landscape. Therefore, I highly recommend exploring the International category on your streaming app to find hidden gems from around the world.",
        ),
        (
            "The Rise of Documentary Series",
            "In recent years, documentary series, or docuseries, have gained massive popularity, often rivaling fictional dramas in viewership. This trend started because people are increasingly interested in real-life mysteries, true crime, and social issues. Unlike traditional documentaries that last only 90 minutes, a series format allows the creators to explore a subject in great detail. Consequently, viewers can see multiple perspectives and understand complex situations that a shorter film might overlook. Furthermore, the high production value of modern docuseries makes them as visually engaging as blockbuster movies. However, some argue that these shows can sometimes sensationalize tragic events for entertainment purposes. In my view, when done ethically, docuseries are an excellent educational tool that can spark important conversations about justice and history. Because they combine facts with emotional storytelling, they are a powerful way to raise awareness about global problems. In conclusion, the truth is stranger than fiction approach is a winning formula for modern television.",
        ),
        (
            "How Social Media Influences Scriptwriting",
            "Social media has a significant impact on how television series are written and produced today. Because fans are constantly sharing their opinions on platforms like X, formerly Twitter, and Reddit, writers receive immediate feedback on their work. Consequently, some showrunners admit that they occasionally adjust the plot or give more screen time to a character based on positive reactions online. Furthermore, series are now designed to be meme-able, with specific lines or visual moments created specifically to go viral. While this can increase a show's popularity, it also carries risks. If writers focus too much on pleasing the fans, the original vision of the story might suffer. In my opinion, the interaction between creators and fans is generally positive, but there must be a limit. A script should be driven by artistic integrity, not by a trending hashtag. Therefore, the best series are those that surprise the audience instead of simply giving them what they expect.",
        ),
        (
            "The Reboot Trend: Nostalgia vs. Innovation",
            "It seems like every famous series from the 90s or 2000s is receiving a reboot or a revival lately. This trend is driven by nostalgia, as production companies know that established fanbases are a safe investment. Because people love to revisit the characters they grew up with, reboots often achieve high ratings in their first episodes. Consequently, we are seeing a wave of old stories returning to the screen with modern updates. However, many critics argue that this focus on the past is stifling innovation in the industry. Instead of taking risks on new ideas, studios prefer to recycle old ones. Furthermore, many reboots fail to capture the magic of the original show, leading to disappointment among fans. In my view, while a well-made revival can be a treat, I would much rather see original stories that reflect our current world. In conclusion, nostalgia is a powerful tool, but it shouldn't replace the need for fresh and diverse voices in television.",
        ),
        (
            "Series as a Tool for Social Change",
            "Television series have the unique power to influence public opinion and promote social change. Because viewers spend dozens of hours with the same characters, they often develop a strong emotional connection with them. Consequently, when a series addresses topics like mental health, racial inequality, or LGBTQ+ rights, it can help reduce stigma and increase empathy. Furthermore, series like The Handmaid's Tale or Black Mirror use dystopian scenarios to warn us about the consequences of our political and technological choices. In my opinion, entertainment should do more than just help us escape reality; it should also make us think critically about it. When a show successfully combines a great plot with a powerful message, it leaves a lasting impact on society. Therefore, we should value and support creators who use their platforms to speak up about important issues. Entertainment is a mirror of our world, and it has the potential to make that world a better place.",
        ),
        (
            "The Mystery of Open Endings in Series",
            "Many modern series choose to end their seasons, or even their entire runs, with open endings that leave many questions unanswered. This technique is often used to create suspense and encourage fans to theorize about what happened next. Consequently, the discussion about the show continues on social media long after the finale has aired. Furthermore, an open ending allows the writers to return for a sequel or a spinoff in the future. However, many viewers find this approach frustrating because they want a clear resolution after investing so much time in the story. In my view, an open ending is successful only if it fits the theme of the series. If it feels like the writers just didn't know how to finish the story, it can ruin the entire experience. In conclusion, a good ending should provide emotional closure, even if every detail isn't perfectly explained. A bit of mystery is fine, but total confusion is usually a mistake.",
        ),
        (
            "The Importance of Soundtracks in Television",
            "The music in a television series is often just as important as the script or the acting. A well-chosen soundtrack can enhance the mood of a scene, build tension during a climax, or even become the identity of a show. For example, the opening themes of series like Game of Thrones or Succession are iconic and instantly recognizable. Furthermore, many series use popular songs to connect with the audience's emotions, often causing old songs to become hits again on Spotify. Consequently, the role of the music supervisor has become one of the most respected jobs in the industry. In my opinion, the best series are those where the music feels like another character in the story. If you remove the soundtrack, the emotional impact is significantly reduced. Therefore, we should pay more attention to the sound design and the score, as they are essential components of the storytelling process.",
        ),
        (
            "Why Sitcoms Are the Ultimate Comfort Food",
            "In times of stress or uncertainty, many people turn to classic sitcoms like Friends, The Office, or Brooklyn Nine-Nine. These shows are often called comfort food because they are predictable, funny, and warm. This happens because the characters usually stay the same, and most problems are solved within twenty minutes. Consequently, watching an old sitcom feels like visiting old friends. Furthermore, the repetitive nature of these shows provides a sense of security that more intense dramas lack. In my view, there is nothing wrong with watching the same episode for the tenth time if it makes you feel better. Sometimes, we don't want a complex plot or a dark mystery; we just want a good laugh and a happy ending. Therefore, sitcoms play a vital role in our mental well-being, proving that television can be a powerful source of joy and relaxation.",
        ),
    ],
}


SERIES_TEXTS["b2"] = [
    (
        "The Ethical Dilemma of True Crime Series",
        "The proliferation of true crime docuseries has sparked a profound ethical debate regarding the boundaries between public interest and exploitative entertainment. While these productions often shed light on judicial failures or unsolved mysteries, they simultaneously run the risk of re-traumatizing the victims' families. The primary concern is that by turning real-life tragedies into bingeable content, the human element is often overshadowed by stylized cinematography and suspenseful editing. Furthermore, the massive popularity of these shows can lead to armchair detectives interfering with ongoing investigations, sometimes with disastrous consequences. In my view, creators have a moral obligation to prioritize the dignity of the victims over the narrative's shock value. We must ask ourselves if our curiosity justifies the commodification of someone else's suffering. As consumers, being mindful of the perspective the series adopts is crucial-does it seek justice, or is it merely capitalizing on the morbid curiosity of the masses?",
    ),
    (
        "The Quality TV Revolution and the Death of the Procedural",
        "In the early 2000s, a shift occurred in the television landscape that critics often refer to as the Golden Age of Television. This era marked a move away from the traditional procedural format-where each episode featured a self-contained story-toward highly serialized, novelistic narratives. Shows like The Wire or Mad Men demanded a higher degree of intellectual engagement from the audience, rewarding those who paid close attention to subtle character arcs and thematic motifs. This transition was facilitated by the rise of cable networks and, eventually, streaming services that weren't beholden to the rigid structures of broadcast television. Consequently, the distinction between cinema and television has become increasingly blurred. However, some argue that in our pursuit of complex prestige dramas, we have lost the simple, episodic charm of traditional TV. Whether this evolution is a definitive improvement or merely a change in fashion remains a subject of intense discussion among media scholars.",
    ),
    (
        "The Psychological Appeal of Dystopian Narratives",
        "Dystopian series such as The Handmaid's Tale or Black Mirror have achieved immense success by tapping into contemporary anxieties regarding political instability and technological overreach. Why are we so drawn to these bleak, often terrifying visions of the future? Psychologists suggest that by engaging with these worst-case scenarios from the safety of our living rooms, we are performing a form of emotional rehearsal for real-world crises. These stories provide a safe environment to explore the ethical limits of our society and the potential consequences of our current trajectory. Furthermore, dystopian fiction often serves as a powerful form of social critique, stripping away the comforts of the present to reveal the underlying fragility of our institutions. In my opinion, the enduring popularity of the genre reflects a collective need to confront our fears rather than ignore them. By visualizing the abyss, we might find the motivation to steer our society toward a more hopeful alternative.",
    ),
    (
        "Subverting Expectations: The Power of the Plot Twist",
        "A well-executed plot twist is perhaps the most exhilarating tool in a screenwriter's arsenal, capable of fundamentally altering the viewer's perception of the entire story. However, in an age where fans meticulously analyze every frame of a series on social media, subverting expectations has become increasingly difficult. The challenge for modern writers is to create a surprise that feels earned rather than forced for shock value. A successful twist should be hidden in plain sight, with clues planted throughout the narrative that only make sense in retrospect. If a twist contradicts the established logic of a character or the world, it risks alienating the audience and undermining the emotional weight of the story. Ultimately, the best plot twists are those that don't just change what happens, but change what the story is about. It requires a delicate balance of foresight and misdirection, proving that television is as much an art of manipulation as it is of representation.",
    ),
    (
        "The Cultural Significance of Fandoms",
        "The relationship between a television series and its audience has evolved from passive consumption to active, organized participation known as fandom. Modern fandoms are not just groups of people who like the same show; they are vibrant digital communities that create fan art, write fiction, and engage in deep philosophical debates about the narrative. This level of engagement can be a powerful force for good, as seen when fans organize charity drives or campaign to save a canceled series. However, the intensity of fandom can also lead to toxic behavior, where fans harass creators or actors if the story doesn't align with their personal desires. This raises interesting questions about authorship: does a story belong to the creator who wrote it, or to the community that loves it? In my view, while fan engagement is a testament to the power of storytelling, it is vital to maintain a boundary that allows artists to pursue their vision without fear of retribution from the very people they seek to entertain.",
    ),
    (
        "Representation Matters: The Shift Toward Diversity",
        "The demand for diverse representation in television series is not merely a matter of political correctness; it is a fundamental shift in how we understand the purpose of media. For decades, the stories told on screen were largely monolithic, excluding the experiences of vast segments of the population. Today, there is a growing recognition that everyone deserves to see themselves reflected in the narratives that shape our culture. Proper representation involves moving beyond tokenism and stereotypes to create multidimensional characters whose identities are integral but not limited to their background. This diversity enriches the industry by introducing fresh perspectives and untapped stories, which in turn attracts a more global and engaged audience. However, the industry still has a long way to go in ensuring that this inclusivity extends behind the camera to writers, directors, and producers. In conclusion, a more representative television landscape is not just more equitable; it is creatively superior and more reflective of the beautiful complexity of the human experience.",
    ),
    (
        "The Binge Model and the Erosion of Narrative Tension",
        "While the all-at-once release model pioneered by streaming services offers unparalleled convenience, it has fundamentally changed the internal pacing of television narratives. When a series is designed to be watched in a single sitting, writers often prioritize immediate hooks over long-term tension. This can lead to what some critics call the saggy middle, where the middle episodes of a season lack a clear identity and serve merely as filler between the beginning and the end. Furthermore, the lack of a weekly release schedule eliminates the communal pause-that period of seven days where audiences can theorize, debate, and let the emotional weight of an episode sink in. Consequently, many modern series feel more like overextended movies than true episodic television. In my opinion, the return to a weekly release model for prestige shows suggests that both creators and audiences are rediscovering the value of anticipation. Sometimes, the space between the episodes is just as important as the episodes themselves.",
    ),
    (
        "The Aesthetic of the Anti-Heroine",
        "While the male anti-hero has been a staple of prestige television for years, we are now seeing a fascinating rise in the anti-heroine. Characters who are difficult, ambitious, and morally compromised-yet undeniably compelling-are finally taking center stage in shows across all genres. This shift is significant because it challenges the traditional likability requirement that has historically been imposed on female characters. By allowing women to be as flawed and complex as their male counterparts, writers are dismantling long-standing gender tropes and offering a more honest portrayal of the female experience. These characters force the audience to confront their own biases regarding power, motherhood, and professional ambition. In my view, the anti-heroine is a vital addition to the television landscape because she proves that a character doesn't need to be nice to be worthy of our attention. True equality in storytelling means having the right to be as complicated, messy, and morally grey as anyone else.",
    ),
    (
        "The Philosophy of the Spinoff",
        "In the current media environment, a successful television series is rarely allowed to simply end; instead, it is often expanded into a cinematic universe through spinoffs, prequels, and sequels. From a business perspective, this is a logical strategy to minimize risk by building on an established brand. However, from a creative standpoint, spinoffs are a philosophical gamble. They raise the question of whether a story's world is rich enough to sustain further exploration, or if the expansion is merely a cynical exercise in profit. A successful spinoff, like Better Call Saul, manages to carve out its own unique identity while enriching the original series. Conversely, a poor spinoff can retroactively diminish the impact of the source material by over-explaining mysteries or diluting the stakes. Ultimately, the expansion of a narrative universe should be driven by a genuine desire to tell a new story, rather than just a desire to keep a lucrative franchise on life support.",
    ),
    (
        "The Nostalgia Trap in Modern Media",
        "Modern television seems to be caught in a persistent nostalgia trap, where reboots and period dramas dominate the production cycle. Whether it's the 1980s aesthetic of Stranger Things or the endless revivals of 90s sitcoms, we are constantly looking backward. While nostalgia can be a powerful emotional tool that provides comfort in an uncertain world, it can also act as a barrier to innovation. If we are constantly recycling the imagery and themes of the past, we are failing to create a distinct aesthetic for the present. Furthermore, nostalgia often provides a sanitized, idealized version of history that ignores the complexities and injustices of the eras it seeks to celebrate. In my opinion, while there is nothing wrong with honoring our cultural heritage, the industry must be careful not to become a museum of the familiar. The most enduring series are often those that take risks and look forward, defining the now rather than just reflecting the then.",
    ),
]


SERIES_TEXTS["c1"] = [
    (
        "The Semiotics of the Small Screen",
        "In the contemporary media landscape, the television series has transcended its origins as mere domestic entertainment to become a primary vehicle for complex semiotic exploration. Unlike the self-contained cinematic experience, the episodic nature of a series allows for a profound layering of motifs and symbols that can be revisited and refined over dozens of hours. This iterative storytelling creates a unique hermeneutic circle between the creator and the audience, where viewers become adept at decoding subtle visual cues and recurring narrative tropes. The nuance of this engagement lies in the slow burn-the deliberate accumulation of tension and meaning that would be impossible within a two-hour timeframe. Furthermore, the aesthetic of the small screen has evolved to favor intimacy over spectacle, utilizing the close-up to navigate the labyrinthine interiority of its characters. As we engage with these protracted narratives, we are not merely spectators but active participants in a process of world-building that mirrors the complexity of our own reality.",
    ),
    (
        "The Architecture of Prestige: Beyond the Script",
        "While the quality of writing is often cited as the hallmark of Prestige TV, the architecture of these productions involves a sophisticated synergy of cinematography, sound design, and art direction that operates on a level of cinematic excellence. The visual grammar of a series like Succession or The Crown is not merely decorative; it is an integral component of the storytelling, articulating power dynamics and emotional states through framing and color theory. The nuance of prestige production lies in its haptic quality-the ability of the image to convey texture and atmosphere so vividly that it evokes a sensory response in the viewer. Moreover, the score often functions as a psychological anchor, utilizing leitmotifs to deepen our understanding of character evolution. To analyze a modern masterpiece of television is to look beyond the dialogue and appreciate the meticulous craftsmanship that constructs its immersive reality. It is this multi-dimensional approach to production that has elevated the medium to its current status as a formidable peer to traditional cinema.",
    ),
    (
        "The Parasocial Paradox: Our Relationship with Fictional Characters",
        "One of the most fascinating aspects of long-form television is the development of parasocial relationships-the one-sided emotional bonds that viewers form with fictional characters. Because we invite these characters into our homes week after week, often for years at a time, our brain processes their triumphs and tribulations with a degree of empathy that can rival our real-world connections. The nuance of this paradox is that while we are intellectually aware of the character's fictionality, our emotional response remains authentically visceral. This phenomenon is amplified by the rise of social media, where fans can discuss a character's life as if they were a mutual acquaintance. However, this deep investment can lead to a sense of betrayal if a character acts out of turn or if a series ends in a way that feels unearned. Understanding the parasocial paradox is essential for creators, as they must balance the need for narrative surprise with the emotional expectations of an audience that feels it knows the characters better than the writers themselves.",
    ),
    (
        "The Cultural Hegemony of the English-Language Narrative",
        "Despite the recent success of international hits, the global television market remains largely under the shadow of an English-language cultural hegemony. The storytelling structures, ethical frameworks, and aesthetic preferences of North American and British productions often dictate the standard for quality worldwide. This dominance is not merely a matter of linguistic convenience; it is a manifestation of soft power that shapes global perceptions of morality, success, and domesticity. The nuance of this hegemony lies in its ability to assimilate and domesticate foreign narratives, often stripping them of their specific cultural contexts to fit a universal, read Western, template. For a truly diverse global media landscape to emerge, we must move beyond mere representation and actively support the sovereignty of diverse storytelling traditions. This requires a critical interrogation of our own viewing habits and a willingness to engage with narratives that challenge the established Western tropes of heroism and resolution.",
    ),
    (
        "The Epistemological Crisis of the Deepfake Era",
        "As the technology behind digital manipulation becomes increasingly sophisticated, the television industry is entering an epistemological crisis regarding the nature of evidence and representation. The emergence of high-fidelity deepfakes and AI-generated actors threatens to undermine our trust in the moving image, making it difficult to distinguish between authentic performance and algorithmic synthesis. The nuance of this crisis extends to the historical narrative; if we can digitally resurrect deceased actors or alter the footage of past events with perfect realism, the sanctity of the historical record is compromised. While these tools offer incredible creative possibilities for science fiction and fantasy, they also provide a potent weapon for disinformation. Creators and audiences alike must develop a new kind of visual literacy to navigate this fragmented reality. The challenge of the coming decade will be to establish ethical and technical safeguards that preserve the integrity of performance in a world where the truth of the image is no longer a given.",
    ),
    (
        "The Sunk Cost Fallacy of Long-Running Series",
        "There is a psychological phenomenon in television viewing known as the sunk cost fallacy, where an audience continues to watch a series that has significantly declined in quality simply because they have already invested so much time in it. This is particularly prevalent in long-running procedurals or sprawling fantasy epics that may have lost their original creative spark. The nuance of this commitment lies in the hope for a return to form or the desire for closure, however unsatisfying it may be. Producers often exploit this loyalty by introducing increasingly sensational plot twists to maintain viewership, a practice colloquially known as jumping the shark. For the critical viewer, identifying the point at which a series has exhausted its narrative potential is an essential skill. True appreciation of the medium involves acknowledging that a story is defined as much by its ending as by its beginning. A series that knows when to conclude its narrative arc with dignity is often more valuable than one that lingers into obsolescence.",
    ),
    (
        "The Subversion of Genre: The Hybridization of TV",
        "In the current Peak TV era, traditional genre boundaries have become increasingly porous, leading to a sophisticated hybridization that defies simple categorization. We are seeing the rise of prestige horror, dark comedy-thrillers, and speculative period dramas that blend disparate elements to create something entirely new. This subversion of genre expectations is a powerful tool for thematic exploration, as it allows creators to tackle complex social issues from unexpected angles. The nuance of this hybridization lies in the cognitive dissonance it produces in the viewer; by placing familiar tropes in unfamiliar contexts, writers can bypass our cynicism and provoke a more visceral emotional response. However, successful hybridization requires a deep understanding of the rules of each genre to subvert them effectively. When done poorly, it results in a tonal mess; when done well, it expands the boundaries of what television can achieve, proving that the medium's greatest strength lies in its infinite capacity for reinvention.",
    ),
    (
        "The Labor Behind the Lens: The Ethics of Production",
        "The glamour of the final product often obscures the intense, and sometimes exploitative, labor that goes into the production of a high-budget television series. From the crunch culture in visual effects houses to the grueling hours of the crew and the precarious nature of gig-economy writing rooms, the ethics of production are a critical concern for the industry. The nuance of this issue is found in the discrepancy between the progressive values often championed on screen and the conservative, bottom-line-driven practices behind the scenes. As audiences become more conscious of social justice, there is a growing demand for transparency and fair labor practices within the entertainment industry. Supporting a series should involve a recognition of the collective effort involved, ensuring that the magic of television is not built upon the burnout or disenfranchisement of its workers. A truly great series is one that respects its creators as much as its consumers, fostering a sustainable environment where creativity can thrive without compromising human dignity.",
    ),
    (
        "The Narrative Efficiency of the Limited Series",
        "The resurgence of the limited series or miniseries format represents a pushback against the never-ending nature of traditional television. By committing to a predetermined number of episodes, creators can craft a narrative with the precision of a novel, ensuring that every scene serves a specific thematic purpose. The nuance of this format is its narrative efficiency-the absence of filler and the intensity of the stakes that come from a guaranteed resolution. This allows for a higher caliber of talent, as high-profile actors and directors are more willing to commit to a short-term project. Furthermore, the limited series is often the ideal vehicle for adapting complex literature, providing enough space to honor the source material without the need to stretch the story to fit a multi-season mandate. In the current landscape of content overload, the limited series offers a curated and satisfying experience that respects the viewer's time and intellectual capacity.",
    ),
    (
        "Television as a Mirror: The Reflexive Nature of Modern TV",
        "Modern television has become increasingly reflexive-meaning that it often comments on its own nature as a medium and its relationship with the audience. Shows like Community, 30 Rock, or The Rehearsal break the fourth wall and deconstruct the tropes of storytelling, inviting the viewer to participate in a meta-commentary on the act of watching. The nuance of this reflexivity is that it doesn't necessarily distance the audience from the story; instead, it creates a deeper level of engagement based on shared cultural knowledge. This meta-humor functions as a form of social bonding, acknowledging the sophisticated media literacy of the 21st-century viewer. However, there is a risk that excessive reflexivity can descend into hollow cynicism or inside jokes that alienate those outside the specific fandom. The most successful reflexive shows are those that use self-awareness to explore deeper truths about the human condition, proving that we can be both conscious of the artifice and moved by the emotion.",
    ),
]


SERIES_TEXTS["c2"] = [
    (
        "The Ontological Shift: Seriality and the Reconfiguration of Temporal Perception",
        "The ascendancy of the serialized narrative in the twenty-first century has precipitated an ontological shift in how the contemporary subject perceives and consumes temporal duration. Unlike the ephemeral nature of the standalone feature film, the protracted engagement required by a multi-season series necessitates a sustained psychological investment that mirrors the unfolding of lived experience. This seriality functions as a temporal architecture, where the diegetic world of the series begins to bleed into the viewer's own reality, creating a persistent, parallel existence. The nuance of this phenomenon resides in the liminality of the binge-watching state-a suspension of external time where the boundaries of the self-become porous, absorbing the rhythms and anxieties of the fictional world. As we navigate these vast narrative expanses, we are not merely observing a story; we are participating in a fundamental reconfiguration of our relationship with time, where the now of the series becomes as significant as the now of the domestic space.",
    ),
    (
        "The Hegemony of the Algorithm: The Aesthetic of Predictive Content",
        "In the contemporary era of the attention economy, the production of television series has become increasingly subservient to the dictates of the predictive algorithm. This shift from curated artistic vision to data-driven content generation represents a profound transformation in the aesthetic landscape of the small screen. Algorithms, designed to maximize retention and engagement, prioritize narrative beats that align with established consumer preferences, effectively creating a feedback loop that stifles genuine innovation. The nuance of this hegemony lies in the subtle homogenization of storytelling; series are increasingly structured around moments designed to go viral, prioritizing immediate emotional impact over the slow, meticulous development of theme and character. This aesthetic of the predictive is characterized by a polished sameness, a visual and narrative fluency that is as frictionless as it is ephemeral. The challenge for the modern creator is to operate within these constraints while reclaiming the serendipitous-the chaotic, unpredictable human elements that defy algorithmic categorization.",
    ),
    (
        "The Ethics of the Simulacrum: Historical Revisionism in Prestige Drama",
        "The proliferation of high-budget historical dramas has reignited a contentious debate regarding the ethics of the simulacrum-a representation that has no original reality but becomes a reality in its own right. As series like The Crown or Chernobyl blur the lines between meticulous research and dramatic license, the audience's perception of history is increasingly mediated by a stylized, narrativized version of the past. The nuance of this revisionism is found in the affective truth-the idea that a fictionalized account can convey the emotional essence of a period even if it diverges from factual accuracy. However, this raises profound epistemological questions: when the simulacrum becomes more vivid and accessible than the historical record, do we risk losing our grasp on the objective past? The responsibility of the creator in this context is gargantuan, as they are not merely entertaining, but actively constructing the collective memory of a generation.",
    ),
    (
        "The Phenomenology of the Anti-Heroine: Transgressing the Likability Mandate",
        "The emergence of the complex anti-heroine in contemporary television represents a significant transgression of the likability mandate that has historically constrained female characters. By allowing women to occupy the same morally ambiguous, often repugnant spaces as their male counterparts, series are dismantling the essentialist tropes of the domestic and the nurturing. The phenomenology of the anti-heroine-exemplified by characters who are ambitious, destructive, and deeply flawed-forces the audience to confront their own subconscious biases regarding gender and power. The nuance of this engagement lies in the uncomfortable empathy it provokes; we are drawn to these characters not despite their flaws, but because of them, recognizing in their transgression a raw, unvarnished humanity. This shift is not merely a matter of representation, but a fundamental expansion of the medium's capacity to explore the darker, more labyrinthine aspects of the female psyche.",
    ),
    (
        "The Death of the Finale: Narrative Exhaustion in the Age of the Franchise",
        "In the current media ecosystem, the finale has become an increasingly rare and problematic concept, as successful narratives are perpetually extended through spinoffs, prequels, and expanded universes. This refusal to grant a story its definitive end is a symptom of a broader narrative exhaustion, where the commercial value of a brand takes precedence over the artistic integrity of its conclusion. The nuance of this phenomenon is the erosion of the catharsis-the emotional release that comes from a well-earned resolution. When a series is denied its closure, it lingers in a state of perpetual adolescence, diluting the stakes and diminishing the impact of its original themes. To truly honor a narrative is to acknowledge its finitude; a story that refuses to end is a story that eventually ceases to mean. The challenge for the discerning viewer is to recognize when a narrative arc has been completed, even if the industry refuses to acknowledge it.",
    ),
    (
        "The Semiotic Labyrinth of the Dystopian Meta-Narrative",
        "Contemporary dystopian series often function as meta-narratives, commenting not just on the world they depict, but on our own consumption of such imagery. This semiotic labyrinth-where the critique of the surveillance state is consumed via a surveillance-heavy streaming platform-creates a profound sense of irony and complicity in the viewer. The nuance of this engagement lies in the reflexive gaze, where the series invites us to scrutinize the very systems that allow it to exist. As we watch the disintegration of social order from the comfort of our living rooms, we are forced to confront our own role as passive observers of real-world crises. This meta-narrative strategy bypasses the audience's cynicism by acknowledging it, creating a sophisticated dialogue regarding the efficacy of art as a tool for social change in a world saturated by the aesthetic of the abyss.",
    ),
    (
        "The Haptic Aesthetic: Texture and Atmosphere as Narrative Agents",
        "In the realm of prestige television, the image has moved beyond its function as a mere carrier of information to become a haptic agent-an image that evokes a sense of touch and physical presence. Through the meticulous use of lighting, production design, and high-definition cinematography, series can convey the grain of a wooden table, the chill of a damp basement, or the stifling heat of a desert afternoon with visceral intensity. This haptic aesthetic is a powerful tool for immersion, bypassing the intellectual center of the brain to provoke a direct sensory response. The nuance of this approach is found in the sensory economy-the idea that atmosphere can convey as much narrative weight as dialogue or action. To watch a modern masterpiece is to feel its reality, a realization that the small screen is capable of an intimacy and a sensory depth that often exceeds the capabilities of traditional cinema.",
    ),
    (
        "The Paradox of Choice: Decision Fatigue and the Erosion of Curation",
        "The sheer volume of content produced by global streaming services has led to a psychological phenomenon known as decision fatigue, where the surplus of choice results in a paralysis of agency. In this environment, the traditional role of the critic or the curator has been largely replaced by the automated recommendations of the algorithm. The nuance of this paradox is the erosion of the serendipitous discovery-the accidental encounter with a masterpiece that falls outside one's established preferences. As we are funneled into increasingly narrow content bubbles, our cultural horizons are subtly constricted. The challenge for the modern viewer is to actively seek out the friction of the unfamiliar, to consciously bypass the ease of the algorithm in favor of a more rigorous, intentional engagement with the medium. True cultural literacy in the digital age requires a proactive resistance to the frictionless path of the recommended for you tab.",
    ),
    (
        "The Ethics of the Gaze: Voyeurism and Complicity in True Crime",
        "The true crime genre operates at a problematic interstice between investigative journalism and morbid voyeurism. By transforming real-world suffering into a consumable narrative, these series invite the audience into a state of complicit observation, where our entertainment is predicated on the exploitation of trauma. The nuance of this ethical dilemma resides in the aestheticization of the crime scene-the use of stylized editing and haunting scores to turn tragedy into a compelling hook. As viewers, we are frequently implicated in the narrative, our curiosity framed as a search for justice while often serving merely as a search for sensation. To engage with true crime with C2-level sophistication is to interrogate our own motivations, to demand a mode of representation that prioritizes the dignity of the victim over the thrill of the reveal. The genre's popularity is a testament to our fascination with the shadow, but it is also a mirror of our own moral compromises.",
    ),
    (
        "The Return to the Mythic: The Archetypal Resonance of Genre Fiction",
        "Despite the move toward gritty realism, contemporary television has seen a resurgence of the mythic-the use of genre fiction, fantasy, science fiction, horror, to explore archetypal truths about the human condition. Series like Game of Thrones or Stranger Things succeed not merely because of their world-building, but because they tap into the collective unconscious, utilizing ancient narrative structures to map the anxieties of the modern world. The nuance of this resonance is the ability of the fantastic to bypass our rational defenses and speak directly to our primal fears and desires. In the struggle between light and shadow, the hero's journey, and the confrontation with the monster, we find a timeless framework for understanding our own fragmented reality. This return to the mythic suggests that in an age of data and transparency, we still crave the mystery and the symbolic depth of the archetypal narrative to make sense of our place in the cosmos.",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, estruturas de repeticao e vocabulario concreto",
    "a1": "rotinas, preferencias, conectores simples e verbos no presente",
    "a2": "passado simples, comparativos e descricoes detalhadas",
    "b1": "opinioes, causa e consequencia, conectores variados",
    "b2": "argumentacao, ideias abstratas e vocabulario avancado",
    "c1": "nuance, estilo, critica cultural e estruturas variadas",
    "c2": "registro erudito, inferencia, ambiguidade e complexidade sintatica",
}


class Command(BaseCommand):
    help = "Replace the Series catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="series")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = SERIES_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-series-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Series texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre series: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D cartoon style, clean lines, high quality, "
            f"educational television series scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
