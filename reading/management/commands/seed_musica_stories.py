import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


MUSIC_TEXTS = {}


MUSIC_TEXTS["iniciante"] = [
    (
        "The Piano in the Room",
        "There is a piano in the living room. The piano is black and white. My brother plays the piano every day. The music is very beautiful and soft. I listen to the piano and I am happy. The keys are cold, but the music is warm. It is a very big instrument. I want to play the piano, too.",
    ),
    (
        "A Red Guitar",
        "This is a red guitar. The guitar has six strings. My friend Clara has a guitar. She plays the guitar in the park. The music is loud and fun. We sing songs together. I like the sound of the guitar. It is a small and light instrument. Playing the guitar is a great hobby.",
    ),
    (
        "The Loud Drums",
        "The drums are in the garage. They are very loud. Boom, boom, boom! My cousin Lucas is a drummer. He hits the drums with two sticks. The rhythm is fast. I move my feet to the music. The drums are big and round. It is an exciting instrument for a rock song.",
    ),
    (
        "Singing in the Shower",
        "I like to sing. I sing in the shower every morning. The water is hot and the music is fun. I have a favorite song on the radio. My voice is not perfect, but I am happy. Singing is good for the heart. My mother hears my voice and she smiles. It is a happy start for my day.",
    ),
    (
        "The Silver Flute",
        "The flute is a silver instrument. It is long and thin. Sarah plays the flute in the school band. The sound of the flute is like a bird. It is very high and sweet. Sarah practices the flute every afternoon. She sits on a chair and breathes deeply. The flute is a beautiful instrument.",
    ),
    (
        "A Radio on the Table",
        "There is a small radio on the kitchen table. The radio plays music all day. I hear pop music and jazz. Sometimes there is news, but I prefer music. The volume is low in the morning. I drink my coffee and listen to the songs. The radio is old, but the music is new.",
    ),
    (
        "Dancing at the Party",
        "Today is a party. The music is very fast and loud. Everyone is dancing in the room. I like to dance with my friends. We move our bodies to the rhythm. The lights are colorful. The music makes us jump and laugh. A party is better with good music. It is a fun night.",
    ),
    (
        "The Violin Lesson",
        "I have a violin lesson today. The violin is a small wood instrument. It has four strings. I use a bow to play the violin. My teacher is very patient. The sound is a bit difficult at first, but I practice. The violin is in a black case. I love my violin music.",
    ),
    (
        "Listening with Headphones",
        "I have blue headphones. I put the headphones on my ears. Now the music is only for me. I listen to music on the bus. I listen to music at the university. The world is quiet, but the music is loud. I like many different singers. Headphones are great for a student.",
    ),
    (
        "A Big Concert",
        "Tonight is a big concert in Brasilia. Many people are at the stadium. There is a famous band on the stage. The lights are bright and the music is powerful. I see the singer and the guitar players. We shout and clap our hands. A concert is a magic experience. I love live music.",
    ),
]


MUSIC_TEXTS["a1"] = [
    (
        "My Daily Soundtrack",
        "I listen to music every single day because it helps me concentrate on my studies. In the morning, I usually play classical music or lo-fi beats while I am coding. These genres are very calm and they don't have many lyrics, so I don't get distracted. However, when I go to the gym in the afternoon, I prefer rock or electronic music because the rhythm is fast and energetic. Music changes my mood completely. If I am sad, I play a happy pop song and I feel much better immediately. I think life is very silent and boring without a good soundtrack.",
    ),
    (
        "Learning an Instrument",
        "My friend Geovanna is learning to play the electric guitar. She practices for one hour every evening after her university classes. She says that learning an instrument is difficult but very rewarding. First, she learned the basic chords and now she can play a few simple songs. She wants to start a band with our classmates next semester. I don't play an instrument, but I am a good singer, so maybe I can be the vocalist. We want to practice in her garage on weekends. Playing music together is a great way to make friends and have fun.",
    ),
    (
        "The Magic of Live Concerts",
        "Last month, I went to a big music festival in the city center. There were many different bands playing at the same time. I love live music because the energy of the crowd is incredible. You can feel the vibration of the drums in your chest. I saw my favorite indie band on the main stage and it was a dream come true. The tickets were a bit expensive, but the experience was worth every cent. I bought a t-shirt with the name of the band to remember that night. Concerts are much more exciting than listening to a CD at home.",
    ),
    (
        "Different Musical Genres",
        "The world of music is very diverse and there is a genre for every person. Some people love jazz because the instruments, like the saxophone and the piano, create a very sophisticated atmosphere. Other people prefer country music because the stories in the lyrics are very emotional and simple. Personally, I like Brazilian Popular Music (MPB) because the melodies are beautiful and the Portuguese lyrics are like poetry. My father likes old rock and roll from the 70s, but my younger brother only listens to trap and hip-hop. It is interesting how music can represent different generations.",
    ),
    (
        "How I Discover New Music",
        "In the past, people discovered new music on the radio or on television. Today, I use streaming apps to find new artists from all over the world. Every Monday, the app creates a special playlist for me with songs I don't know yet. If I like a song, I save it to my Favorites folder. I also follow some music influencers on YouTube who talk about new albums and music history. Because of technology, I can listen to a singer from Japan or a band from Iceland in seconds. It is amazing how the internet made music more accessible for everyone.",
    ),
    (
        "The Importance of Lyrics",
        "For many people, the melody is the most important part of a song, but I pay a lot of attention to the lyrics. I think that lyrics are like short stories or poems. Some songs talk about love and happiness, while others discuss social problems or personal challenges. When I listen to a song in English, I always check the translation to understand the message. This is also a very good way to learn new vocabulary and expressions. A song with powerful lyrics can stay in your head for a long time and make you think about life.",
    ),
    (
        "Music in the Kitchen",
        "In my house, music is always playing in the kitchen during dinner time. My mother loves to listen to Italian songs while she is cooking pasta. She says that music makes the food taste better! Sometimes, we all dance together while we wait for the meal. It is a very happy tradition in our family. We have a small Bluetooth speaker on the shelf. My father prefers instrumental music during dinner because he says it is more relaxing for conversation. I agree with him, but sometimes a loud pop song is more fun. Music brings our family together.",
    ),
    (
        "Street Musicians",
        "When I walk to the university, I often see street musicians playing in the subway station. Some play the violin, and others have a full set of drums. I always stop for a minute to listen because they are very talented. I usually leave some coins in their instrument cases to show my support. These musicians make the city more beautiful and less stressful. I think it is very brave to play music for strangers in public. One day, a man was playing the cello and the sound was so moving that I almost cried. Street music is a gift for the city.",
    ),
    (
        "Why I Love Vinyl Records",
        "My grandfather has a large collection of vinyl records in his office. He says that the sound of a record is warmer and more authentic than digital music. I like the ritual of choosing a record, cleaning it, and putting the needle on the disc. The covers are also very big and have beautiful artwork. It is a very different experience from just clicking a button on a phone. Sometimes, the record has some small noises, but my grandfather says that is the soul of the music. Now, I am starting my own collection of vinyl records too.",
    ),
    (
        "Music and Exercise",
        "I cannot imagine going for a run without my headphones. I have a specific playlist for exercise with very fast and loud songs. This type of music gives me the adrenaline I need to finish the last kilometer. When the rhythm matches my steps, I feel like I have more power in my legs. Scientific studies say that music can improve athletic performance and reduce the feeling of tiredness. After my run, I switch to ambient music to help my body relax. Music is the perfect partner for any physical activity because it keeps you motivated.",
    ),
]


MUSIC_TEXTS["a2"] = [
    (
        "My First Music Festival",
        "Last summer, I traveled to a large music festival in the countryside with my friends. It was much more crowded than the local concerts I usually attend in Brasilia. We arrived early because we wanted to see the opening act, which was a new folk band. In my opinion, the lead singer's voice was even more beautiful in person than on the recordings. We stayed until the very end, and the final performance was the loudest and most energetic show I ever saw. The weather was hotter than we expected, but we drank plenty of water and had an amazing time. Compared to listening to music at home, the festival atmosphere was significantly more intense. I felt more connected to the artists and the crowd. It was definitely the highlight of my year.",
    ),
    (
        "The Evolution of My Musical Taste",
        "When I was younger, I only listened to pop music because it was what my friends liked. I thought other genres, like jazz or classical music, were more boring and difficult to understand. However, five years ago, I started playing the piano, and my teacher introduced me to different styles. I realized that classical music is actually more complex and emotional than modern pop. Now, my playlist is much more diverse than it was in the past. I enjoy discovering how rock music from the 70s influenced the indie bands I like today. My taste is more sophisticated now because I appreciate the technical skills of the musicians. It is interesting to see how we change as we grow older and learn more about art.",
    ),
    (
        "A Nostalgic Night at the Opera",
        "Last month, my grandmother invited me to go to the opera for the first time. I was a bit nervous because I thought it would be less interesting than a movie or a musical. The theater was older and more elegant than any place I visited before. When the orchestra started playing, the sound was more powerful than I imagined. The singers didn't use microphones, but their voices were louder and clearer than the instruments. Even though I didn't understand all the lyrics, the story was easier to follow than I expected. I felt like I traveled back in time to the 19th century. The experience was more magical than a regular concert, and I promised my grandmother that we would go again next season.",
    ),
    (
        "Buying My First Record Player",
        "Two weeks ago, I finally bought a vintage record player for my bedroom. I always thought that digital music was more convenient, but my father told me that vinyl sounds better. He was right! The sound of a record is warmer and more authentic than a digital file. I went to a small music shop and bought two old rock albums. They were cheaper than I thought, and the covers were much more beautiful than the small icons on my phone. Setting up the record player was more difficult than using a streaming app, but the process was very rewarding. Now, I spend my Saturday mornings listening to music in a more relaxed way. For me, the physical experience of music is more special than just clicking a button.",
    ),
    (
        "The High School Battle of the Bands",
        "Last year, our university organized a Battle of the Bands competition. Four different groups of students performed on a stage in the central hall. The first band was a metal group, and they were much louder than the others. The second group played acoustic covers, and their performance was more peaceful and melodic. My favorite was the third band because they played original songs that were more creative than the covers. The judges decided that the last band was the winner because their stage presence was better. It was a very exciting evening, and it proved that our classmates are more talented than we realized. I hope they organize the event again next semester because it brought everyone together.",
    ),
    (
        "A Street Performer in Europe",
        "When I traveled to Portugal two years ago, I saw a street performer playing the harp in a public square. I never saw a harp so close before, and it was much larger than I thought. The music was more delicate and enchanting than the typical guitar players I see in the subway. Many people stopped to listen, and the atmosphere became more quiet and respectful. I stayed there for twenty minutes because the melodies were more relaxing than the noise of the city. I gave the musician some money because her performance was more professional than many concerts I paid for in the past. It was one of the most memorable moments of my trip because it was an unexpected gift of art.",
    ),
    (
        "Comparing Acoustic and Electric Guitars",
        "Recently, I started taking guitar lessons, and I had to choose between an acoustic or an electric guitar. My teacher explained that an acoustic guitar is better for beginners because it is simpler to carry and you don't need an amplifier. However, I think the electric guitar is more versatile because you can change the sound with different pedals. The electric guitar I tried at the shop was heavier than the acoustic one, but it was also more fun to play. In the end, I bought the acoustic guitar because the sound is more natural and woody. It was a difficult choice, but I am happy with my decision. I hope that in the future, when I am a better player, I can buy an electric one too.",
    ),
    (
        "The Mystery of the Lost Song",
        "Last night, I remembered a song that my mother used to sing to me when I was a child. I didn't remember the name of the artist or the title, so I tried to find it online. Searching for a song with only a few words is more frustrating than I expected! I spent two hours listening to different artists from the 80s. Finally, I found a video on YouTube, and the melody was exactly as I remembered. Listening to it again made me feel more nostalgic and happier than I was before. The lyrics were simpler than I thought, but the emotional connection was very strong. It is amazing how a single song can be more powerful than a thousand words when it comes to memories.",
    ),
    (
        "A Rainy Day with Jazz",
        "Last Sunday, it rained all day in Brasilia, so I stayed home and listened to jazz music. I usually prefer faster songs, but the slow rhythm of the saxophone was more appropriate for the weather. I felt more calm and focused on my studies than usual. I discovered a new artist who is more famous in Europe than in Brazil. His style is more modern than traditional jazz, and the piano parts are very sophisticated. I realized that jazz is the perfect soundtrack for a quiet day. Compared to my usual pop music, this genre is more intellectual and helps me think more clearly. Now, I have a special playlist for rainy days.",
    ),
    (
        "Why I Prefer Small Concerts",
        "A few months ago, I went to a stadium concert, and last week, I went to a small jazz club. I realized that I prefer the small club because the experience is more intimate. In the stadium, the singer was more distant, and I had to watch the screens to see her face. In the club, I was closer to the stage, and the sound was more real and less processed. The tickets for the club were also much cheaper than the stadium seats. Although the big show had more lights and special effects, the small concert felt more personal and authentic. In my opinion, the quality of the music is more important than the size of the production.",
    ),
]


MUSIC_TEXTS["b1"] = [
    (
        "The Streaming Revolution: Convenience vs. Fair Pay",
        "The advent of streaming services has undeniably changed the way we consume music. In the past, people had to buy physical albums or digital files, which meant that artists received a direct profit from every sale. Today, however, because we pay a small monthly fee for unlimited access, the revenue for individual musicians has decreased significantly. Consequently, many independent artists struggle to make a living solely from their recordings. On the positive side, streaming has made music discovery much easier. Because of sophisticated algorithms, listeners can find new bands from across the globe with a single click. Furthermore, it has eliminated the problem of digital piracy, as streaming is more convenient than illegal downloading. In my opinion, while the convenience for the consumer is fantastic, the industry must find a more equitable way to compensate creators. Therefore, supporting your favorite artists by attending their live shows or buying their merchandise is essential for their survival in this new digital landscape.",
    ),
    (
        "Why Vinyl is Making a Comeback",
        "It is fascinating to observe that in an age of high-definition digital audio, vinyl records are experiencing a massive resurgence in popularity. This trend is driven by a desire for a more tangible and authentic connection with music. Because digital files are invisible and ephemeral, many fans feel that something is missing from the experience. Consequently, they are turning to vinyl because it offers a physical ritual: the act of holding the sleeve, reading the liner notes, and carefully placing the needle. Furthermore, many audiophiles argue that vinyl provides a warmer and more organic sound than compressed digital formats. In my view, the return of vinyl is a reaction against the fast-paced nature of modern life. It encourages us to sit down and listen to an entire album from start to finish, rather than skipping tracks on a playlist. Therefore, despite being an old technology, vinyl remains a powerful symbol of artistic intentionality and slow consumption.",
    ),
    (
        "The Power of Music in Mental Health",
        "Music is far more than just a form of entertainment; it is a profound tool for emotional regulation and mental well-being. Scientific studies have shown that listening to certain melodies can trigger the release of dopamine in the brain. Consequently, music therapy is now frequently used to treat patients with anxiety, depression, and even memory loss. For instance, classical music is often recommended for concentration, whereas upbeat pop songs can improve motivation during difficult tasks. Furthermore, the act of playing an instrument or singing in a choir fosters a sense of community and self-expression. In my opinion, we often underestimate the therapeutic power of a good playlist. Because music bypasses the rational mind and speaks directly to our emotions, it can provide comfort when words are not enough. Therefore, integrating music into our daily self-care routine is a simple but highly effective way to maintain psychological balance in a stressful world.",
    ),
    (
        "How TikTok is Shaping Modern Hit Songs",
        "In recent years, social media platforms like TikTok have become the primary drivers of success in the music industry. Because the platform relies on short, catchy videos, songs are often written with a specific viral moment in mind. Consequently, many modern hits feature simple, repetitive hooks that work well in a fifteen-second clip. This has led to a significant change in songwriting structures, where the chorus often appears much earlier than in traditional tracks. Furthermore, TikTok allows old, forgotten songs to become global hits again overnight due to a trending dance or challenge. While this provides great opportunities for new artists to be discovered, some critics argue that it reduces the artistic depth of music. In my view, the platform has democratized the industry, but writers should be careful not to sacrifice their creativity just to satisfy an algorithm. In conclusion, social media is a double-edged sword that has permanently altered the relationship between artists and their audience.",
    ),
    (
        "The Cultural Importance of Music Festivals",
        "Music festivals like Glastonbury or Coachella are more than just series of concerts; they are major cultural events that foster a sense of collective identity. Because people from different backgrounds gather in one place for several days, these festivals create a unique temporary community. Consequently, attendees often feel a profound sense of freedom and belonging that is difficult to find in daily life. Furthermore, festivals provide a vital platform for emerging artists to reach a massive audience. However, the commercialization of these events has led to extremely high ticket prices, which some argue makes them elitist. In my opinion, despite the high costs, the cultural value of experiencing live music in a communal setting is irreplaceable. It allows us to disconnect from our screens and share a visceral, human experience. Therefore, festivals will likely continue to thrive as long as people crave real-world connections and shared artistic moments.",
    ),
    (
        "The Role of Background Music in Productivity",
        "The debate over whether music helps or hinders productivity is a common topic among students and professionals. For many, silence is essential for deep concentration; however, others find that background music helps them enter a flow state. This usually happens because music can mask distracting environmental noises, such as traffic or distant conversations. Consequently, many offices and study halls now allow the use of headphones to improve focus. Furthermore, instrumental genres like lo-fi or ambient music are particularly effective because they provide a consistent rhythm without the distraction of lyrics. In my view, the effectiveness of music depends entirely on the nature of the task. If you are performing a repetitive job, upbeat music can prevent boredom. Conversely, if you are learning a new language or solving complex math, total silence might be superior. Therefore, understanding your own cognitive patterns is key to choosing the right soundtrack for your work.",
    ),
    (
        "Why We Still Need Music Education in Schools",
        "Despite budget cuts in many countries, music education remains a vital part of a well-rounded school curriculum. Learning to read music and play an instrument stimulates the brain in ways that few other subjects can. Consequently, students who study music often show better performance in mathematics and spatial reasoning. Furthermore, participating in a school orchestra or band teaches essential life skills such as discipline, teamwork, and patience. In my opinion, music is a universal language that allows children to express emotions that they might not be able to put into words. If we remove music from schools, we are depriving the next generation of a fundamental tool for cognitive and emotional development. Therefore, we should view music education not as a luxury, but as a necessity for a healthy and creative society. In conclusion, the benefits of music go far beyond the classroom and stay with a person for their entire life.",
    ),
    (
        "The Environmental Impact of the Music Industry",
        "When we think of pollution, we rarely think of music, yet the industry has a significant environmental footprint. In the past, the production of millions of plastic CDs and vinyl records created a large amount of physical waste. Today, although streaming has reduced plastic use, the massive data centers required to host millions of songs consume enormous amounts of electricity. Consequently, our digital habits contribute to carbon emissions in a way that many people don't realize. Furthermore, global tours by major artists involve private jets and thousands of trucks, which has a massive ecological impact. In my view, both artists and fans need to be more conscious of these issues. Some bands are now trying to organize green tours by using renewable energy and banning single-use plastics at venues. Therefore, as consumers, we should support artists who prioritize sustainability and push the industry toward a more eco-friendly future.",
    ),
    (
        "The Art of Film Scoring: Music as a Narrator",
        "A film without music would feel empty and emotionally flat because the soundtrack often acts as an invisible narrator. Film composers use specific instruments and melodies to tell the audience how to feel. For instance, high-pitched violins create tension in a thriller, while a warm piano might signal a moment of romance. Consequently, a great film score can make a scene iconic, even without any dialogue. Furthermore, music can bridge the gap between different cultures by using traditional instruments to ground the story in a specific location. In my opinion, the best composers are those whose music supports the story without distracting from the actors. If you pay close attention to the soundtrack next time you watch a movie, you will realize how much the music influences your perception of the plot. Therefore, film scoring is an essential art form that deserves as much recognition as directing or acting.",
    ),
    (
        "Music as a Form of Social Protest",
        "Throughout history, music has been one of the most powerful tools for social and political change. Because a song can be easily memorized and shared, it can spread a message of protest far more effectively than a speech or a pamphlet. Consequently, genres like folk, reggae, and hip-hop have often been the voice of marginalized communities fighting for justice. For example, during the civil rights movement, songs provided strength and unity to those marching for equality. Furthermore, music allows artists to criticize those in power in a way that is both artistic and accessible to the public. In my view, the most enduring songs are often those that challenge the status quo and demand a better world. Therefore, we should respect the role of the protest singer as a vital guardian of democracy and human rights. In conclusion, music is not just a background noise; it is a catalyst for reflection and action.",
    ),
]


MUSIC_TEXTS["b2"] = [
    (
        "The Ethical Dilemma of AI in Musical Composition",
        "The integration of Artificial Intelligence into the creative process of musical composition has sparked a polarizing debate within the artistic community. On one hand, AI tools can analyze vast datasets of existing music to assist composers in generating complex harmonies and innovative structures that might have been overlooked by the human ear. Consequently, these technologies are being embraced as a powerful collaborator that can democratize music production for those without formal training. On the other hand, many critics argue that music generated by algorithms lacks the soul and the lived emotional experience that defines true art. Furthermore, significant concerns regarding copyright and intellectual property have been raised, as AI models are often trained on the work of human artists without their explicit consent. In my opinion, if we continue to prioritize efficiency over authenticity, we risk devaluing the very labor that makes music meaningful. While AI is an impressive tool, it should remain a supplement to human creativity rather than a replacement for it.",
    ),
    (
        "The Physics of Sound: Understanding Resonance and Timbre",
        "To truly appreciate music, one must understand the fundamental physics of sound, specifically the concepts of resonance and timbre. Every musical instrument produces sound through vibrations; for instance, when a guitar string is plucked, it vibrates at a specific frequency, creating a pitch. However, the reason a piano sounds different from a flute, even when playing the same note, lies in timbre or tone quality. This is determined by the overtones or harmonics that accompany the fundamental frequency. Consequently, the materials used to build an instrument-such as the type of wood in a violin or the alloy in a trumpet-are critical to its acoustic signature. Furthermore, the space in which music is performed plays a vital role, as sound waves reflect off surfaces to create reverberation. In my view, the intersection of science and art is where the magic of music resides. If we ignore the physical properties of sound, we fail to recognize the meticulous engineering required to achieve auditory perfection.",
    ),
    (
        "The Global Rise of K-Pop: A Lesson in Cultural Branding",
        "The meteoric rise of K-Pop (South Korean Pop) to global dominance is a fascinating case study in the intersection of traditional music, modern performance, and aggressive digital branding. Unlike traditional Western groups, K-Pop idols undergo years of rigorous training in vocals, dance, and language before their debut. Consequently, their performances are characterized by a level of synchronization and visual perfection that is rarely matched in other markets. Furthermore, the industry has mastered the art of fan engagement through social media, creating a powerful sense of community that transcends national borders. However, some argue that the factory-like nature of the production system can be detrimental to the artists' mental health and creative autonomy. In my opinion, the success of K-Pop proves that music is no longer just an auditory experience; it is a multi-sensory brand. While the music itself is often catchy and well-produced, it is the holistic package that has captivated a global generation.",
    ),
    (
        "The History of the Blues: From Suffering to Influence",
        "The Blues is arguably the most influential genre in the history of modern music, serving as the foundational DNA for rock and roll, jazz, and even hip-hop. Originating in the Deep South of the United States among African American communities, the Blues was born out of a history of struggle, oppression, and resilience. The classic 12-bar blues structure and the use of blue notes-notes played at a slightly lower pitch than the standard scale-create a distinct emotional tension. Consequently, the music became a powerful medium for storytelling and social commentary. Furthermore, the transition from acoustic to electric blues in cities like Chicago paved the way for the high-energy performances of the mid-20th century. In my view, without the raw honesty of the Blues, contemporary music would lack much of its emotional depth. It is a reminder that the most enduring art often emerges from the most difficult human experiences.",
    ),
    (
        "The Evolution of Recording Technology: From Tape to Digital",
        "The history of music is inextricably linked to the evolution of recording technology, which has fundamentally changed how we create and listen to sound. In the early days of analog recording, musicians had to perform perfectly in a single take on magnetic tape. Consequently, the process was labor-intensive and required a high degree of technical precision. The introduction of multi-track recording in the 1960s allowed artists like The Beatles to layer sounds and experiment with complex arrangements. However, the real revolution occurred with the shift to digital recording, or DAWs, which allows for infinite editing and manipulation of sound. While digital technology has made recording more accessible and affordable, some purists argue that it has led to an over-sanitized sound, where small human errors are corrected by software. In my opinion, the best recordings are those that balance modern clarity with the warmth and character of traditional methods.",
    ),
    (
        "The Impact of Globalization on Traditional Musical Heritage",
        "As the world becomes increasingly interconnected, traditional musical styles are facing both new opportunities and significant threats. Globalization has allowed local genres, such as Reggaeton from the Caribbean or Afrobeat from Nigeria, to reach a massive international audience. Consequently, these styles are influencing mainstream pop music in unprecedented ways. However, there is a risk that this global exposure leads to cultural dilution, where traditional instruments and rhythms are modified to fit a Western commercial template. Furthermore, as younger generations in developing countries adopt global pop trends, ancient musical traditions are at risk of being forgotten. In my view, we must strive for a balance between innovation and preservation. If we do not actively document and support traditional musicians, we may lose the unique cultural fingerprints that have defined communities for centuries. Diversity in music is as important as biodiversity in nature.",
    ),
    (
        "Syncopation and the Concept of Rhythm in Jazz",
        "At the heart of the feeling of jazz music lies the concept of syncopation-the deliberate displacement of the regular beat to create unexpected accents. Unlike classical music, which often follows a more predictable meter, jazz thrives on the tension between what the listener expects and what is actually played. Consequently, this creates a sense of swing that encourages physical movement and dance. Furthermore, the role of improvisation in jazz requires musicians to have a deep understanding of harmonic theory and an intuitive connection with their fellow performers. This musical conversation is what makes every jazz performance unique. In my opinion, jazz is the most sophisticated form of American art because it values individual expression within a collective framework. If you learn to appreciate the complexity of a syncopated rhythm, you begin to understand the true meaning of musical freedom.",
    ),
    (
        "The Commercialization of Subcultures in Music",
        "Many musical genres, such as punk and grunge, began as rebellious subcultures that actively rejected mainstream values and corporate control. However, history shows that once a subculture gains popularity, it is inevitably recuperated or commercialized by the major music labels. Consequently, the original message of protest is often diluted into a fashion statement or a marketable aesthetic. For example, the anti-establishment ethos of punk was eventually used to sell high-end clothing and mainstream albums. Furthermore, the rise of fast-music on streaming platforms has accelerated this process, where genres are created and discarded by the industry in a matter of months. In my view, while commercial success can provide a platform for artists, it often comes at the cost of their artistic integrity. The challenge for a modern musician is to stay true to their roots while navigating an industry that views subculture as just another product.",
    ),
    (
        "The Psychology of the Earworm: Why Songs Get Stuck in Our Heads",
        "Most people have experienced the phenomenon of an earworm-a catchy fragment of a song that repeats uncontrollably in the mind. Psychologists call this Involuntary Musical Imagery, or INMI. Research suggests that certain musical characteristics, such as a fast tempo and a simple but slightly unusual melodic contour, make a song more likely to become stuck. Consequently, advertisers and pop producers often use these hooks specifically to ensure their music lingers in the consumer's memory. Furthermore, earworms often occur during periods of low cognitive load, such as when we are walking or doing chores. In my opinion, while earworms can be annoying, they demonstrate the brain's profound sensitivity to rhythm and pattern. It is as if the mind is hard-wired to process music, even when we are not consciously listening. Understanding the mechanics of the earworm can help songwriters create more memorable, though perhaps more intrusive, hits.",
    ),
    (
        "Music and the Architecture of Silence",
        "The famous composer Claude Debussy once said that music is the space between the notes. This concept emphasizes the importance of silence and dynamics in musical storytelling. Without silence, music would be a relentless wall of sound, lacking emotional contrast and narrative structure. Consequently, the most powerful moments in a symphony or a rock ballad are often the pauses or the sudden shifts in volume. Furthermore, the use of negative space in music allows the listener's imagination to participate in the experience. In my view, modern music production often ignores this principle, with many songs being limited to be as loud as possible at all times-a trend known as the Loudness War. If we do not respect the silence, we lose the ability to create true tension and release. Therefore, we should value composers and producers who understand that sometimes, the most important thing to play is nothing at all.",
    ),
]


MUSIC_TEXTS["c1"] = [
    (
        "The Semiotics of Sound: Decoding Musical Meaning",
        "Music, often heralded as a universal language, operates through a complex semiotic system that conveys meaning far beyond the literal translation of its lyrics. This system is predicated on musical signifiers-specific intervals, timbres, and rhythms that evoke culturally encoded emotional responses. For instance, the use of a minor third interval in Western tradition is almost instinctively associated with melancholy, a phenomenon that is not inherently biological but rather a result of centuries of cultural conditioning. The nuance of this semiotic engagement lies in its polysemy-the ability of a single melody to hold multiple, often contradictory, meanings for different listeners. Furthermore, the context of a performance-be it a dimly lit jazz club or a sterile concert hall-functions as a secondary signifier that dictates the audience's behavioral and emotional expectations. To truly read a piece of music is to engage with these layers of symbolism, recognizing that every note is a choice that reflects a specific historical and cultural vantage point.",
    ),
    (
        "The Architecture of Sound: Acoustics and the Performance Space",
        "The relationship between music and the space in which it is performed is a fundamental, yet frequently overlooked, aspect of the auditory experience. The physical architecture of a venue-its materials, dimensions, and shape-functions as a silent instrument that shapes the timbre and clarity of every note. For example, the soaring cathedrals of the Renaissance were designed to enhance the resonance of Gregorian chants, creating a sense of divine permanence through their long reverberation times. Conversely, the dry, intimate acoustics of a modern recording studio allow for the clinical precision required in electronic music production. The nuance of this relationship is the feedback loop between the composer and the environment; many historical styles were explicitly written to exploit the unique acoustic properties of specific venues. Consequently, when we listen to a symphony in a space for which it was not intended, we are experiencing a fragmented version of the artist's original vision. Architecture, in this sense, is not just a container for sound, but a vital participant in its creation.",
    ),
    (
        "The Ethics of the Digital Resurrection",
        "The emergence of hologram concerts and AI-generated vocal tracks has introduced a profound ethical dilemma regarding the digital resurrection of deceased artists. Through sophisticated motion capture and vocal synthesis, technicians can now create new performances by icons like Whitney Houston or Maria Callas, allowing fans to experience a simulacrum of a live show. While proponents argue that this democratizes access to musical history, critics view it as a form of necro-capitalism-the exploitation of a person's image and labor long after their death. The nuance of this debate involves the concept of artistic intent; if a performer is no longer able to consent to the presentation of their work, does the digital representation infringe upon their human dignity? Furthermore, these synthetic performances threaten to displace living artists, as audiences are funneled toward the familiar nostalgia of the past rather than the innovations of the present. We must ask ourselves if we are preserving a legacy or merely haunting the future with the ghosts of a commodified past.",
    ),
    (
        "The Political Power of the Sonic Landscape",
        "Sound is never neutral; it is an active force in the construction of social and political power. The concept of the sonic landscape refers to the totality of sounds that define a specific environment and the power dynamics that dictate who is allowed to be heard. For instance, the use of loud, abrasive music in public spaces-often called sonic weaponry-has been used to disperse protesters or discourage homeless populations from gathering. Conversely, the suppression of indigenous musical traditions by colonial powers was a deliberate strategy to erase cultural identity and enforce hegemony. The nuance of this power dynamic lies in sonic resistance, where marginalized communities reclaim their space through the volume and rhythm of their music. Whether through the defiant boom of a sub-bass or the communal singing of a protest anthem, music functions as a claim to visibility and agency. To understand the politics of a city, one must listen to the sounds that are celebrated and the voices that are systematically silenced.",
    ),
    (
        "The Death of the Album in the Age of the Playlist",
        "The traditional album-a curated sequence of songs designed to be heard as a cohesive narrative-is facing an existential crisis in the era of algorithm-driven streaming. Because listeners now primarily consume music via curated playlists or random shuffle, the structural integrity of the long-form record is being eroded. Consequently, many artists are shifting their focus toward the production of stand-alone singles that are engineered for immediate impact and viral potential. The nuance of this shift is the loss of narrative depth; an album allows a composer to explore a theme with a degree of nuance and development that is impossible within the constraints of a single three-minute track. Furthermore, the lack of a physical object-the sleeve, the liner notes, the artwork-disconnects the music from its visual and tactile context. While the playlist offers unparalleled variety, it often lacks the intentionality of a masterfully paced album. We are gaining convenience, but we may be losing the ability to engage with music as a structured, intellectual journey.",
    ),
    (
        "The Aesthetics of Imperfection: Lo-fi and the Human Touch",
        "In a world characterized by the sterile perfection of digital audio, there is a growing aesthetic movement toward lo-fi (low-fidelity) music, which deliberately incorporates imperfections like tape hiss, background noise, and slightly out-of-tune instruments. This trend is a reaction against the over-produced sound of mainstream pop, which critics argue has been autotuned into oblivion. The nuance of the lo-fi aesthetic is that it utilizes flaws as a signifier of authenticity and intimacy. By revealing the human touch behind the production-the sound of a chair creaking or a fingers sliding across a string-lo-fi creates a sense of vulnerability that resonates with the listener's own experience of imperfection. This movement highlights a fundamental paradox of modern art: the more technology allows us to achieve perfection, the more we crave the organic, the flawed, and the tangible. Perfection, it seems, is less interesting than the honest record of a human struggling with their tools.",
    ),
    (
        "Cultural Appropriation vs. Appreciative Hybridity",
        "The history of music is a history of cultural exchange, yet the line between appreciative hybridity and exploitative appropriation is notoriously difficult to define. The nuance of this debate involves the power dynamics inherent in the exchange; when a dominant culture adopts the musical elements of a marginalized group for commercial gain-often without credit or compensation-it perpetuates a cycle of colonial exploitation. However, some of the most innovative genres in history, such as Jazz and Flamenco, were born from the collision of diverse cultures. The challenge for the modern composer is to engage with foreign traditions with a degree of humility and scholarship that respects the source material. This requires moving beyond the exoticism of the surface-using a sitar or a tribal rhythm for mere flavor-and understanding the deep historical and social context of the sounds. True hybridity should be a dialogue, not a monologue of the powerful.",
    ),
    (
        "The Neurobiology of Musical Memory and Identity",
        "Music has a unique ability to survive even the most severe forms of neurological decline, often remaining accessible to patients with advanced Alzheimer's long after their linguistic and social memories have faded. This suggests that musical memory is encoded in a more robust, distributed network within the brain than other forms of information. The nuance of this phenomenon is that music is not just something we know, it is something that defines us. A specific song can act as a mnemonic key, unlocking a flood of sensory details from a person's past-the smell of the air, the color of the light, the emotional state of a specific moment. Consequently, music therapy is being increasingly recognized as a powerful tool for maintaining a sense of self in the face of cognitive loss. For the individual, our personal soundtrack is the scaffolding upon which our identity is built; if you change the music, you change the person's perception of their own history.",
    ),
    (
        "The Commercialization of Subversive Genres",
        "The trajectory of genres like Punk, Grunge, and Hip-Hop follows a predictable pattern: they begin as raw, subversive expressions of social discontent and eventually end up as sanitized, marketable products for the mainstream. This process, known as recuperation, involves stripping a genre of its political teeth while retaining its visual aesthetic. The nuance of this commercialization is that it creates a spectacle of rebellion-a safe way for the consumer to feel edgy without actually challenging the status quo. Furthermore, once a subversive style is adopted by major labels, the underground scenes that birthed it are often priced out of their own neighborhoods. However, some argue that this mainstreaming is a form of progress, as it forces subversive ideas into the public consciousness. The challenge for the authentic artist is to find a way to navigate the industry without becoming a parody of their own protest.",
    ),
    (
        "The Minimalism of Sound: Silence as a Creative Choice",
        "In an era of constant connectivity and auditory clutter, the use of minimalism and silence in music has become a radical act of resistance. Composers like John Cage and Arvo Part have demonstrated that silence is not the absence of music, but its most profound component. The nuance of this approach is that it forces the listener to become an active participant in the soundscape, focusing their attention on the most minute details of timbre and vibration. Minimalism challenges the Western obsession with progress and climax, favoring instead a state of meditative stasis. By stripping away the non-essential, minimalist music creates a space for reflection that is increasingly rare in our over-stimulated world. This aesthetics of less reminds us that the most powerful experiences often come from the simplest gestures. Silence is not a void to be filled; it is the canvas upon which all sound is given meaning.",
    ),
]


MUSIC_TEXTS["c2"] = [
    (
        "The Ontological Resonance: Music as the Architecture of Being",
        "To contemplate music at its most profound level is to engage with the very scaffolding of human ontology. Beyond its manifestation as a mere sequence of rhythmic vibrations, music functions as a temporal architecture that reconfigures our perception of existence. This ontological resonance suggests that sound is not something we simply observe, but a medium through which we inhabit the world. The nuance of this engagement resides in the liminality of the musical experience-that precise threshold where the physical properties of acoustics dissolve into the metaphysical realm of emotion and memory. Unlike the spatial arts, music's inherent ephemerality mirrors the transience of the self; it exists only in the act of vanishing. Consequently, the listener is forced into a state of radical presence, a confrontation with the now that is simultaneously anchored in the echoes of the past and the anticipation of the future.",
    ),
    (
        "The Hegemony of the Diatonic: A Critique of Western Harmonic Sanity",
        "The global dominance of the Western diatonic scale-the familiar twelve-tone system-represents a form of cultural hegemony that has systematically marginalized alternative modes of sonic organization. This harmonic sanity imposes a rigid structural logic that prioritizes resolution and consonance, often at the expense of the microtonal nuances found in non-Western traditions. The nuance of this critique lies in the realization that our ears have been colonized to perceive certain intervals as inherently correct or natural. To break free from this hegemony is to embrace the dissonant-the sounds that defy the predictive algorithms of Western theory. This is not merely an aesthetic choice, but a subversive act of intellectual liberation. By exploring the in-between frequencies, we rediscover a vast, uncharted territory of human expression that has been silenced by the relentless march of standardized tuning.",
    ),
    (
        "The Phenomenology of the Virtuoso: Performance as Transcendence",
        "The figure of the virtuoso occupies a unique space in the cultural imaginary, representing the pinnacle of human technical achievement and the potential for transcendence through labor. However, a C2-level analysis must look beyond the spectacle of speed and dexterity to examine the phenomenology of the performance itself. The nuance of virtuosity is found in the erasure of the tool-that sublime moment where the instrument is no longer an external object, but an extension of the performer's biological being. In this state of flow, the distinction between the self and the sound collapses, creating a unified field of artistic intention. Yet, there is a tragic dimension to this mastery; the more perfect the performance, the more it highlights the inevitable fragility of the human organism. The virtuoso's struggle is a metaphor for the human condition: a relentless pursuit of the infinite within the finite constraints of flesh and bone.",
    ),
    (
        "The Semiosis of Silence: The Negative Space of Composition",
        "In the frantic noise of the digital age, we frequently neglect the profound semiotic power of silence-the negative space that gives form and meaning to all sound. Silence is not a vacuum; it is a deliberate compositional choice that functions as a linguistic punctuation, a breath, or a terminal point of reflection. The nuance of silence lies in its generative potential-it is the silence before the note that creates tension, and the silence after the note that allows for the resonance of meaning. Composers who understand this architecture of absence invite the listener to participate in the creative process, filling the void with their own internal echoes. To ignore silence is to succumb to a horror vacui that dilutes the emotional impact of the music. A masterpiece is defined as much by what is withheld as by what is expressed, proving that the most eloquent statements are often those that remain unspoken.",
    ),
    (
        "The Aesthetics of Decay: Lo-fi, Nostalgia, and the Ghost of the Analog",
        "The contemporary fascination with the aesthetic of decay-manifested in the deliberate degradation of audio quality through lo-fi filters and tape hiss-reveals a deep-seated cultural anxiety regarding the sterile perfection of the digital. This hauntology seeks to evoke a past that never truly existed, utilizing the ghosts of analog technology to anchor the listener in a sense of nostalgic comfort. The nuance of this trend is the commodification of failure; we deliberately introduce noise and distortion to signify authenticity, turning technical flaws into artistic virtues. This reflects a collective yearning for the tangible-a desire for an art that bears the physical marks of time and usage. In a world where everything is perfectly replicable and eternally new, the cracked, the hissed, and the faded become the ultimate signifiers of a lived, human history.",
    ),
    (
        "The Biopolitics of the Soundscape: Auditory Control and Resistance",
        "Sound is an instrument of biopolitics, a means through which power is exercised over the bodies and minds of a population. The concept of the soundscape is inextricably linked to the regulation of public space, where certain sounds are sanctioned as civilized and others are criminalized as noise. The nuance of this power dynamic is found in the use of music as a tool for social engineering-from the pacifying muzak of shopping malls to the aggressive sonic dispersal of political dissent. To exist in a city is to be subject to a constant, often invisible, auditory management. However, there is always sonic resistance-the disruptive power of the unauthorized rhythm, the subversive volume of the counter-culture, and the radical act of deep listening. Reclaiming the soundscape is a prerequisite for reclaiming social agency; it is the right to define the auditory environment in which we live and breathe.",
    ),
    (
        "The Myth of the Universal Language: Deconstructing Musical Essentialism",
        "The ubiquitous claim that music is a universal language is a seductive myth that masks the profound cultural specificities of musical meaning. While the physical sensation of vibration may be universal, the interpretation of those vibrations is a highly localized, learned behavior. The nuance of this deconstruction lies in the cultural untranslatability of certain musical emotions; what signifies triumph in one tradition may signify lament in another. To insist on a universal meaning is to commit a form of epistemic violence that erases the unique histories and social contexts of diverse sonic practices. Music is not a language of fixed definitions, but a fluid field of potential meanings that requires a specific cultural literacy to decode. True appreciation of global music begins with the humble acknowledgment of our own tonal parochialism and a willingness to engage with the other on its own aesthetic terms.",
    ),
    (
        "The Algorithmic Muse: The Death of the Genius in the Age of AI",
        "The rise of AI-driven composition threatens to dismantle the Enlightenment ideal of the solitary genius, the divinely inspired creator who brings forth original art from the void. In the age of the algorithmic muse, creativity is reframed as an act of pattern recognition and statistical probability. The nuance of this transition is the erosion of artistic intentionality-the why behind the what. While an AI can generate a technically flawless symphony, it lacks the lived experience of suffering, joy, and mortality that historically fueled the creative impulse. Consequently, we are entering an era of aesthetic abundance but emotional scarcity, where the market is flooded with perfectly curated content that possesses no soul. The challenge for the future is to redefine humanity in art: is it found in the perfection of the output, or in the beautifully flawed process of the creator?",
    ),
    (
        "The Metaphysics of the Record: Memory, Stasis, and the Captured Moment",
        "The invention of recording technology effected a metaphysical rupture in human history, allowing us to freeze time and separate sound from its source. The record is a paradox: a captured moment that is simultaneously dead and eternally alive. The nuance of this phenomenon is the stasis it imposes on the artistic work; a recorded performance becomes the definitive version, stifling the fluid, improvisational nature of live music. We have become a culture of collectors rather than listeners, prioritizing the possession of the object over the experience of the event. Furthermore, the ability to repeat a performance infinitely alters our relationship with the sublime; that which was once a rare, unrepeatable revelation is now a background commodity. The record is a mirror of our desire for immortality-a desperate attempt to preserve the ephemeral against the inevitable march of silence.",
    ),
    (
        "The Theology of the Coda: Resolution, Finitude, and the Final Note",
        "Every musical composition is a meditation on finitude, a journey that finds its meaning only in its conclusion-the coda. The theology of the coda resides in the tension between the desire for resolution and the fear of ending. In the final bars of a symphony, we experience a symbolic death, a reconciliation with the silence from which the music emerged. The nuance of this resolution is that it is never truly final; the echo of the last note continues to vibrate in the listener's consciousness, bridging the gap between the artwork and the world. A successful coda does not merely stop; it completes, transforming the preceding chaos into a structured, meaningful whole. This mirrors our own existential longing for a meaningful conclusion to our lives. Music, in its pursuit of the final, perfect cadence, is a practice for the ultimate silence that awaits us all.",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, estruturas de repeticao e vocabulario concreto",
    "a1": "generos, preferencias, conectores simples e verbos de acao e sentimento",
    "a2": "passado simples, comparativos e descricoes de eventos",
    "b1": "opinioes, argumentacao, causa e consequencia, conectores variados",
    "b2": "analise critica, teoria, industria e vocabulario tecnico",
    "c1": "nuance, estilo, critica cultural e inferencia avancada",
    "c2": "registro erudito e literario, ambiguidade e densidade fenomenologica",
}


class Command(BaseCommand):
    help = "Replace the Musica catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="musica")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = MUSIC_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-musica-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Musica texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre musica: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D cartoon style, clean lines, high quality, "
            f"educational music scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
