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
        "The Morning Coffee",
        """I wake up at seven o'clock every morning. First, I go to the kitchen. I make a hot cup of coffee. I like my coffee with a little milk and no sugar. The coffee smells very good. I sit by the window and watch the sun. This is my favorite part of the day. Now, I am ready to start my work.""",
    ),
    (
        "Going to the Supermarket",
        """Today is Saturday. I need to go to the supermarket. I have a small list in my hand. I need bread, eggs, apples, and rice. The supermarket is very big and busy. I find the apples in the fruit section. They are red and sweet. I pay at the cashier and go home. My bags are heavy, but I am happy.""",
    ),
    (
        "At the Bus Stop",
        """I wait for the bus every afternoon. The bus stop is near my house. Usually, the bus is on time. I look at my watch. It is four o'clock. The bus arrives and I get on. I have my ticket in my pocket. I sit near the window and listen to music. The bus ride is twenty minutes. I go to the university.""",
    ),
    (
        "A Rainy Afternoon",
        """It is raining today. I stay at home. I wear my warm sweater and gray socks. I look at the rain through the window. The sky is dark and the streets are wet. I read a book and drink hot tea. I do not want to go out. The house is very quiet and comfortable. I like rainy days when I am inside.""",
    ),
    (
        "Cleaning the House",
        """Sunday is the day to clean the house. I wash the dishes in the kitchen. Then, I clean the floor with water. My brother helps me. He cleans the windows. We listen to the radio while we work. The house is very clean and fresh now. We are tired, but it is good to live in a clean place. Now, we can rest.""",
    ),
    (
        "Cooking Dinner",
        """I am in the kitchen now. I want to cook dinner for my family. I have chicken and potatoes. First, I cut the potatoes. Then, I put the chicken in the oven. It smells delicious! My mother helps me with the salad. We sit at the table at eight o'clock. We talk and eat together. Dinner is a very special time for us.""",
    ),
    (
        "A Walk in the Park",
        """Every evening, I walk in the park with my dog, Max. The park is green and beautiful. Max likes to run on the grass. I see many people. Some people run and some people sit on the benches. The sun is orange and the air is fresh. Walking is very good for my health. Max is a very happy dog in the park.""",
    ),
    (
        "Buying New Clothes",
        """I am at the mall today. I want a new blue shirt for my internship. I go to a clothing store. I see many shirts, but I like the blue one. It is not very expensive. I try the shirt on. It is a perfect fit! I pay with my card and put the shirt in a bag. I am very happy with my new clothes.""",
    ),
    (
        "At the Pharmacy",
        """I have a headache today. I go to the pharmacy near the bank. The pharmacist is very kind. I ask for some medicine. He gives me a small box. I pay and go home. I drink a glass of water with the medicine. I need to rest for one hour. I hope I feel better soon. Health is very important.""",
    ),
    (
        "Using the Computer",
        """I sit at my desk and turn on my computer. I need to check my emails and study. I use the keyboard and the mouse. I look at the screen for a long time. I am a student of Analysis and Systems Development. The computer is very important for my studies and my work. I learn many new things every day on the internet.""",
    ),
]


STORY_TEXTS["a1"] = [
    (
        "A Busy Monday Morning",
        """Every Monday, my alarm clock rings at 6:30 a.m. I usually stay in bed for five minutes, but then I have to get up. First, I take a quick shower and get dressed for my internship at Americanas. After that, I always have a healthy breakfast with fruit and yogurt. I am going to take the bus today because my car is at the mechanic. On the bus, I usually read my English notes or check my emails on my phone. Monday is always the busiest day of the week, but I like the energy of the office.""",
    ),
    (
        "My Weekend Plans",
        """This weekend is going to be very relaxing. On Saturday morning, I am going to clean my bedroom and organize my university books. In the afternoon, I am going to meet my friend Geovanna at a cafe in the city center. We are going to talk about our classes and our favorite series. On Sunday, I never wake up early. I usually stay at home and cook a special lunch for my family. In the evening, I am going to watch a movie and prepare my things for Monday. I love weekends because I have time for myself.""",
    ),
    (
        "At the Coffee Shop",
        """I often go to the coffee shop near the university during my break. When I arrive, I usually wait in line for a few minutes. The barista is very friendly and he knows my name. I always order a large latte and a toasted sandwich. Sometimes, I sit at a table near the window and use the free Wi-Fi to study Python. Today, the shop is very crowded and noisy, so I am going to take my coffee to the park. It is a very simple part of my routine, but it makes me feel very happy and productive.""",
    ),
    (
        "A Visit to the Doctor",
        """I am going to visit the doctor this afternoon because I am feeling very tired lately. First, I need to call the clinic to confirm my appointment. Then, I am going to take the subway to the medical center. I usually wait in the reception area for fifteen minutes. The doctor is going to ask me questions about my diet and my sleep habits. I think I need to drink more water and exercise more often. After the appointment, I am going to buy some vitamins at the pharmacy. Taking care of my health is very important for my studies.""",
    ),
    (
        "Grocery Shopping List",
        """I need to buy many things at the supermarket today because my fridge is empty. First, I am going to write a list so I don't forget anything. I need to buy chicken, eggs, milk, and a lot of vegetables for the week. I am also going to look for some snacks like crackers and chocolate. I usually go to the supermarket on Tuesday nights because it is quieter than on weekends. I am going to pay with my credit card and use my own reusable bags. I always try to buy fresh food to cook healthy meals at home.""",
    ),
    (
        "Helping a Friend Move",
        """Tomorrow morning, I am going to help my cousin move to a new apartment. He has many heavy boxes and some furniture. We are going to start very early, at 8:00 a.m. First, we are going to put the boxes in the truck. Then, we are going to drive to the new building. It is going to be a very long and tiring day, but I am happy to help him. After the work, we are going to order some pizza and celebrate his new home. Helping friends and family is a natural part of my life.""",
    ),
    (
        "Learning a New Recipe",
        """Tonight, I am going to try a new recipe for dinner. I found a video on YouTube about how to make a traditional Italian pasta. First, I am going to boil the water and cook the noodles. While the pasta is cooking, I am going to prepare a fresh tomato sauce with garlic and onions. I usually cook simple meals, but today I want to make something different and delicious. My parents are going to arrive at 7:30 p.m., so I need to be ready. I hope the food tastes good! Cooking is a very creative hobby.""",
    ),
    (
        "An Afternoon at the Library",
        """The university library is my favorite place to focus. I usually go there three times a week after my classes. The atmosphere is very silent and perfect for concentration. Today, I am going to finish a project about database management. First, I find a quiet desk with a power outlet for my laptop. Then, I put on my noise-canceling headphones. I am going to stay here for three hours. Sometimes, I take a small break to drink water or walk a little. The library helps me be a better student and a more organized person.""",
    ),
    (
        "Preparing for a Job Interview",
        """I have a very important job interview next Friday. I am very excited but also a little nervous. This week, I am going to practice my answers and research the company online. I am also going to choose my best clothes for the interview. First, I am going to read my resume again to remember all my technical skills. Then, I am going to ask my brother to help me with a mock interview. I am going to be very professional and confident. Getting a new internship is my main goal for this semester.""",
    ),
    (
        "A Rainy Day Routine",
        """When it rains in Brasilia, the traffic usually gets very bad. Today, it is raining a lot, so I am going to stay at home and work remotely. I always start my day with a hot cup of tea on rainy mornings. First, I check my task list on the computer. Then, I start coding and solving some bugs in my project. I like the sound of the rain outside while I am working. In the afternoon, I am going to take a nap and then continue my studies. Rainy days are perfect for being productive inside the house.""",
    ),
]


STORY_TEXTS["a2"] = [
    (
        "A Better Way to Commute",
        """In the past, I always traveled to work by bus. It was a very long and stressful journey because the traffic in the city center was always worse than I expected. However, last month, I decided to buy an electric scooter. It was one of the best decisions of my year! Now, my commute is much faster and more enjoyable. I can see the trees and feel the fresh air while I am riding. Also, the scooter is more ecological than a car or a bus. Yesterday, it started to rain while I was going home, so I had to stop at a cafe. I drank a hot chocolate and waited for the rain to stop. Even with the rain, I prefer my scooter because I have more freedom and I am never late for my internship anymore.""",
    ),
    (
        "Learning to Cook at Home",
        """Before the pandemic, I never cooked my own meals. I usually ate at the university cafeteria or ordered fast food because it was more convenient. But last year, I decided to learn how to cook healthy food. At first, it was more difficult than I thought. I burned my first omelet and the rice was too salty! However, I practiced every weekend and watched many tutorials. Now, my cooking is much better than before. Last night, I invited my friend Geovanna for dinner and I made a delicious lasagna. She said it was better than the lasagna at the local restaurant! Cooking at home is cheaper and healthier than eating out. I feel more energetic and I am proud of my new skills.""",
    ),
    (
        "A Weekend at the Farmer's Market",
        """Last Sunday morning, I visited the local farmer's market for the first time. It was much busier and more colorful than the regular supermarket. There were many farmers selling fresh fruits, vegetables, and handmade bread. The smell of the strawberries was more intense than the ones I usually buy. I bought some organic honey and a large bag of oranges. While I was walking, I saw an old man playing the violin. The music was more beautiful than the songs on the radio. I stayed there for an hour and talked to some local producers. It was a very relaxing morning. Compared to the supermarket, the market is more social and the food is much fresher. I am going to go there every weekend from now on.""",
    ),
    (
        "Fixing a Technical Problem",
        """Yesterday afternoon, while I was working on my Django project, my laptop suddenly turned off. I felt more frustrated than a person in a long line! I tried to turn it on again, but the screen was black. First, I checked the power cable, but it was okay. Then, I called my brother because he is better at hardware than me. He told me to wait for ten minutes and try again. While I was waiting, I read a book to calm down. Finally, the laptop started working again. It was just a small overheating problem. I realized that I need to clean my desk and keep my laptop cool. It was a stressful hour, but I learned that sometimes you just need to wait and stay calm to solve a problem.""",
    ),
    (
        "My First Day at the Internship",
        """I started my management internship at Americanas three months ago. I remember my first day very clearly. I was more nervous than a student before a big exam! When I arrived, my manager showed me the office and introduced me to the team. Everyone was very kind and helpful. At first, the software system was more complex than the ones I used at the university. I had to ask many questions and take many notes. But after two weeks, I felt more confident. Now, I can handle many tasks alone and I am learning a lot about operations. My internship is more challenging than my classes, but it is also more exciting. I am very happy to work in a real professional environment.""",
    ),
    (
        "A Change in My Routine",
        """Two years ago, I didn't have a very healthy routine. I usually stayed awake until 2 a.m. playing games or watching series. Consequently, I was always tired during the day and my concentration was worse. Last semester, I decided to change my habits. Now, I always go to bed at 10 p.m. and I wake up at 6 a.m. to exercise. At first, the change was more difficult than I imagined, and I missed my late-night games. But now, I feel much more productive and happy. My skin looks better and my grades at the university are higher. A good sleep routine is the most important thing for a student. I realized that the morning is the best time to study and code.""",
    ),
    (
        "Losing and Finding My Wallet",
        """Last Friday, while I was shopping at the mall, I realized that my wallet was not in my bag. I felt more panicked than ever before! My ID, my credit cards, and some money were inside. First, I went back to the last store I visited, but the clerk said she didn't see anything. Then, I went to the Lost and Found office. I was more worried every minute. While I was waiting, a young boy arrived with my wallet in his hand! He found it near the cinema. I was so happy and relieved. I offered him some money as a reward, but he didn't accept it. He was the kindest person I met that week. Now, I am more careful with my bag when I go out.""",
    ),
    (
        "The Best Birthday Gift",
        """For my last birthday, my parents gave me a very special gift: a professional mechanical keyboard. It is much better and more comfortable than my old plastic keyboard. The keys are noisier, but the typing experience is more satisfying. I use it every day for my software engineering projects and my English studies. My brother says the lights on the keyboard are too bright, but I think they are beautiful. Since I started using it, I can type faster and with fewer mistakes. It was the most useful gift I ever received. Sometimes, a good tool makes your work much more pleasant. I am very grateful to my parents for this amazing surprise.""",
    ),
    (
        "A Rainy Trip to the Pharmacy",
        """Last Tuesday, I had a very bad cold. I needed to buy some medicine, but it was raining harder than usual. I didn't have an umbrella, so I wore my waterproof jacket and walked to the pharmacy. The streets were more flooded than I expected. When I arrived, the pharmacy was more crowded than a bus at 6 p.m. Everyone was looking for cold medicine and vitamins! I waited for twenty minutes and finally bought my things. On my way back, I stepped in a large puddle and my shoes got very wet. It was the most uncomfortable walk of the month. When I got home, I took a hot shower and drank some soup. I felt much better after a long sleep.""",
    ),
    (
        "Comparing Two Neighborhoods",
        """I moved to a new neighborhood last month. My old neighborhood was noisier and busier because it was near a main avenue. There were many cars and the air was more polluted. My new neighborhood, however, is much quieter and greener. There is a small park near my house where I can walk my dog every evening. The people here are friendlier and more relaxed than in my old place. However, the supermarkets here are more expensive and the bus stop is more distant. Even with these problems, I prefer my new home. I can sleep better and I feel safer. Sometimes, a quiet environment is more important than a convenient location.""",
    ),
]


STORY_TEXTS["b1"] = [
    (
        "The Challenges of Urban Mobility",
        """Living in a large city like Brasilia or Sao Paulo brings many opportunities, but it also presents significant challenges regarding urban mobility. Because the population is growing rapidly, the public transportation system often struggles to keep up with the demand. Consequently, many people choose to drive their own cars, which leads to massive traffic jams during rush hour. In my opinion, the government should invest more in subway lines and dedicated bike paths. If we had a more efficient train system, fewer people would feel the need to use their cars every day. Furthermore, heavy traffic causes not only delays but also high levels of stress and air pollution. Therefore, improving how we move around the city is essential for our quality of life. We must find sustainable solutions, such as carpooling or electric buses, to ensure that our cities remain habitable for future generations.""",
    ),
    (
        "The Digital Nomad Lifestyle",
        """With the rise of remote work, many professionals are choosing to become digital nomads. This means they can work from anywhere in the world as long as they have a stable internet connection. In my view, this lifestyle offers an incredible sense of freedom and flexibility. However, it is not as easy as it looks on social media. One of the main consequences of moving constantly is the difficulty of maintaining long-term relationships and a stable routine. Furthermore, digital nomads must be very disciplined with their time management. If they don't set strict boundaries between work and leisure, they might end up working more hours than they would in a traditional office. Despite these challenges, I believe that the experience of living in different cultures is invaluable. Therefore, if you have the opportunity to work remotely, you should try it at least once to expand your horizons.""",
    ),
    (
        "The Importance of Financial Literacy",
        """Many young adults start their professional lives without a basic understanding of financial literacy. Consequently, they often struggle with debt or fail to save for the future. In my opinion, schools should include financial education in their curriculum from an early age. If students learned how to create a budget and understand interest rates, they would be much more prepared for the real world. Furthermore, knowing how to invest small amounts of money can lead to significant financial security over time. We must realize that managing money is not just about math; it is about making conscious choices. For instance, instead of buying things impulsively, we should ask ourselves if the purchase is a want or a need. Therefore, being financially literate is one of the most important skills for achieving independence and peace of mind in our daily lives.""",
    ),
    (
        "The Social Pressure of Social Media",
        """Social media has become an inseparable part of our daily routine, but it also creates a lot of social pressure. Because people usually post only the best moments of their lives, many viewers feel that their own lives are boring or unsuccessful. Consequently, this comparison trap can lead to anxiety and low self-esteem. In my view, we should be more mindful of our digital consumption. We must remember that what we see on a screen is often a filtered and edited version of reality. Furthermore, taking digital detox breaks is essential for our mental health. If we spent more time connecting with people in real life and less time scrolling through feeds, we would probably feel much happier. Therefore, while social media is a great tool for communication, we must learn to use it in a healthy way that doesn't compromise our well-being.""",
    ),
    (
        "Sustainable Habits in the Kitchen",
        """Reducing waste in the kitchen is one of the easiest ways to live a more sustainable life. One of the primary causes of environmental problems is the massive amount of food that goes to waste every day. To solve this, we should plan our meals carefully and buy only what we actually need. Consequently, we would save money and reduce our ecological footprint. Furthermore, we should try to avoid single-use plastics by using glass containers or beeswax wraps. In my opinion, small changes in our routine can have a big impact if everyone participates. For instance, composting organic waste instead of throwing it in the trash is a great way to help the planet. Therefore, being a conscious consumer is not just a trend; it is a responsibility that we all must accept to protect the environment.""",
    ),
    (
        "The Art of Time Management for Students",
        """Balancing university classes, an internship, and a social life is a difficult task for most students. The main cause of stress among young people is often a lack of effective time management. Consequently, many students leave their projects for the last minute, which results in poor grades and exhaustion. In my view, using a digital planner or a physical notebook is essential for staying organized. We should prioritize our tasks using the Eisenhower Matrix, focusing on what is important and urgent first. Furthermore, we must learn to say no to distractions, such as excessive social media use. If we managed our time more efficiently, we would have more hours for rest and hobbies. Therefore, mastering our schedule is the key to a successful academic career and a balanced personal life.""",
    ),
    (
        "Navigating Workplace Etiquette",
        """Starting a new job or internship requires more than just technical skills; it also requires an understanding of workplace etiquette. Because every company has its own culture, we must observe how colleagues interact and communicate. For instance, some offices are very formal, while others are more relaxed. In my opinion, being punctual and respectful is the most important rule in any professional environment. Furthermore, we should be careful with our digital communication; emails should be clear and professional. If you have a problem with a coworker, you should try to resolve it through a private and calm conversation. Consequently, you will build a reputation as a reliable and professional person. Therefore, understanding these unwritten rules is essential for a long and successful career in any field, including software engineering.""",
    ),
    (
        "The Benefits of Learning a Second Language",
        """Learning a language like English is no longer just an academic requirement; it is a global necessity. One of the main consequences of being bilingual is the ability to access a vast amount of information and career opportunities. For example, in the tech industry, most documentation and new technologies are published in English first. Consequently, if you speak English, you can learn new skills much faster than someone who doesn't. Furthermore, traveling becomes a much richer experience when you can communicate with people from different backgrounds. In my view, the process of learning a language also improves our cognitive abilities and problem-solving skills. Therefore, we should see language learning as a lifelong journey rather than a chore. It is an investment in ourselves that will always pay off in the future.""",
    ),
    (
        "Dealing with Information Overload",
        """In the digital age, we are constantly bombarded with news, notifications, and data. This phenomenon is known as information overload, and it can be very overwhelming. The main cause is the constant connectivity provided by our smartphones. Consequently, many people find it difficult to focus on a single task for a long time. In my opinion, we should practice information filtering. This means choosing only a few reliable sources of news and turning off non-essential notifications. Furthermore, we must learn to embrace boredom occasionally, as it is often during quiet moments that our best ideas emerge. If we don't control the flow of information, it will control us. Therefore, creating a quiet space in our daily routine is essential for maintaining our mental clarity and focus.""",
    ),
    (
        "The Importance of Community and Volunteering",
        """In our increasingly individualistic society, the sense of community is often lost. However, participating in local events or volunteering for a cause can be incredibly rewarding. One of the main benefits of volunteering is the opportunity to meet people outside our usual social circle. Consequently, it helps us develop empathy and a broader perspective on life's challenges. In my view, we should all try to contribute a few hours of our time to help others, whether it's at a local food bank or a community garden. Furthermore, helping others has been shown to reduce stress and improve our own happiness. If everyone did a small act of kindness every week, our neighborhoods would be much safer and friendlier places. Therefore, being an active part of a community is essential for a meaningful and connected life.""",
    ),
]


STORY_TEXTS["b2"] = [
    (
        "The Architecture of Open-Plan Offices",
        """The design of modern workspaces has shifted significantly over the last decade, with many companies adopting open-plan offices to foster collaboration and transparency. Proponents argue that by removing physical barriers, employees are more likely to engage in spontaneous brainstorming sessions. However, recent studies suggest that this layout often results in a paradoxical decrease in productivity. The constant noise and visual distractions, which are inherent in such environments, frequently lead to cognitive overload. Consequently, many workers now use noise-canceling headphones as a digital wall to reclaim their focus. In my opinion, while the intention behind open offices is noble, the lack of privacy can be detrimental to deep work. If a company values innovation, it must provide a variety of spaces, including quiet zones and private pods, to accommodate different working styles.""",
    ),
    (
        "The Gentrification of Urban Neighborhoods",
        """Gentrification is a complex socioeconomic phenomenon that occurs when higher-income residents move into historically lower-income neighborhoods. While this process often leads to improved infrastructure, safer streets, and new businesses, it also results in the displacement of long-term residents. As property values and rents rise, the original inhabitants, who are often the cultural heart of the area, find themselves priced out of their own homes. Consequently, the unique character of the neighborhood is frequently replaced by generic commercial chains. In my view, urban development should be inclusive rather than exclusive. If the government implemented stricter rent controls and invested in social housing, the benefits of revitalization could be shared by everyone. Therefore, we must strive for a balance between modernizing our cities and preserving the social fabric that makes them vibrant.""",
    ),
    (
        "The Psychological Trap of Fast Fashion",
        """The rise of fast fashion has revolutionized the way we consume clothing, making trendy items available at incredibly low prices. However, this convenience comes with a staggering environmental and ethical cost. The industry is responsible for significant carbon emissions and the exploitation of labor in developing nations. The nuance of the problem lies in the psychological tactics used by retailers, such as creating a sense of artificial scarcity to encourage impulsive purchases. Consequently, clothes are often treated as disposable items, worn only a few times before being discarded. In my opinion, we must transition toward a circular economy where quality is prioritized over quantity. If consumers were more aware of the lifecycle of their garments, they might choose to invest in sustainable brands. Ultimately, conscious consumption is the only way to mitigate the ecological impact of our wardrobes.""",
    ),
    (
        "The Evolution of the Gig Economy",
        """The gig economy, characterized by short-term contracts and freelance work mediated by digital platforms, has fundamentally altered the traditional employment landscape. For many, it offers a level of flexibility that was previously unimaginable, allowing individuals to balance multiple projects and set their own schedules. However, this autonomy often comes at the expense of job security and social benefits. Workers in the gig economy are frequently classified as independent contractors, which means they lack access to health insurance, paid leave, and retirement plans. Consequently, there is a growing debate about the need for new labor regulations that protect these precarious workers. In my view, while the gig economy facilitates innovation, it must not become a mechanism for eroding workers' rights. We must ensure that the digital revolution in labor is both fair and sustainable.""",
    ),
    (
        "The Ethics of Data Privacy in Daily Life",
        """In our hyper-connected world, we constantly exchange personal data for the convenience of using free digital services. From our location history to our shopping preferences, every movement is tracked and monetized by large tech corporations. The challenge lies in the lack of transparency regarding how this data is stored and utilized. Many users are told that their information is anonymized, yet sophisticated algorithms can often re-identify individuals with startling accuracy. Consequently, the boundary between public and private life is becoming increasingly blurred. In my opinion, data privacy should be treated as a fundamental human right rather than a luxury. If we do not demand stricter regulations and more robust encryption, we risk living in a society where our every thought and action is predicted and manipulated by invisible entities.""",
    ),
    (
        "Navigating Intercultural Communication in Business",
        """As the global market becomes more integrated, the ability to navigate intercultural communication has become a critical professional skill. Misunderstandings often arise not from language barriers, but from deep-seated cultural differences in how people perceive hierarchy, time, and directness. For instance, in some cultures, a yes might actually mean I understand, rather than I agree. Consequently, failing to recognize these nuances can lead to failed negotiations and strained partnerships. In my view, cultural intelligence requires active listening and a willingness to suspend judgment. If a professional takes the time to learn the etiquette and values of their international counterparts, they are far more likely to build lasting trust. Therefore, diversity should be seen as an asset that, when managed with empathy, can lead to more creative and effective problem-solving.""",
    ),
    (
        "The Impact of Remote Work on Mental Health",
        """The widespread adoption of remote work has been hailed as a major victory for work-life balance, yet its long-term impact on mental health is a cause for concern. While the elimination of the daily commute is a significant benefit, the lack of physical interaction with colleagues can lead to feelings of isolation and professional loneliness. Furthermore, the always-on culture of digital communication makes it difficult for employees to disconnect from their responsibilities. Consequently, the home, once a sanctuary, can become a source of constant stress. In my opinion, companies must implement the right to disconnect policies to protect their employees' well-being. If we do not establish clear boundaries between our professional and personal lives, the benefits of remote work will be overshadowed by a surge in burnout and anxiety.""",
    ),
    (
        "The Rise of Prosumerism and the End of Passive Consumption",
        """The traditional boundary between producers and consumers is dissolving, giving rise to the prosumer-an individual who both consumes and creates content or products. This shift is most evident on platforms like YouTube, TikTok, and Etsy, where ordinary people can reach global audiences. Consequently, consumers are no longer passive recipients of marketing; they are active participants who influence brand narratives. This democratization of production is empowering, but it also creates a saturated market where attention is the scarcest resource. In my view, the rise of the prosumer reflects a desire for more authentic and personalized experiences. If traditional companies want to survive, they must learn to collaborate with their audience rather than just selling to them. The future of the economy lies in co-creation and community engagement.""",
    ),
    (
        "The Paradox of Choice in the Modern Market",
        """We live in an era of unprecedented choice, from the hundreds of cereals in the supermarket to the thousands of movies on streaming platforms. While we are told that more choice leads to more freedom, psychologists argue that it often leads to decision paralysis and decreased satisfaction. When faced with too many options, we worry about making the wrong choice, which leads to post-purchase regret. Consequently, many people find themselves overwhelmed by the sheer volume of decisions they must make every day. In my opinion, we should practice intentional simplification by limiting our options to a few high-quality sources. If we spent less time comparing minor details and more time focusing on our core values, we would be much happier. Therefore, true freedom is not the ability to choose everything, but the wisdom to know what truly matters.""",
    ),
    (
        "The Role of Critical Thinking in the Age of Misinformation",
        """In the digital age, we are constantly exposed to a torrent of information, much of which is biased, misleading, or entirely fabricated. The ease with which fake news can spread on social media has created a crisis of truth that threatens democratic institutions. Consequently, the ability to practice critical thinking is no longer just an academic skill; it is a civic necessity. We must learn to evaluate the credibility of sources, recognize logical fallacies, and be aware of our own cognitive biases. In my view, the education system must prioritize media literacy to prepare students for the complexities of the modern information landscape. If we do not learn to distinguish fact from fiction, we will remain vulnerable to manipulation and polarization. Therefore, an informed and skeptical citizenry is the strongest defense against the erosion of shared reality.""",
    ),
]


STORY_TEXTS["c1"] = [
    (
        "The Erosion of the Third Place",
        """Sociologists have long emphasized the importance of the Third Place-social environments separate from the two primary spheres of home and work-as essential anchors of community life. However, in the contemporary urban landscape, these spaces are increasingly being commodified or altogether eradicated. Where once local libraries and public squares provided a venue for unmediated social interaction, we now find a proliferation of pseudo-public spaces, such as shopping malls and corporate-owned plazas, where presence is contingent upon consumption. The nuance of this shift lies in the subtle policing of behavior that occurs within these commercialized realms; those who do not possess the requisite purchasing power are often subtly, yet firmly, excluded. Consequently, the social fabric is becoming increasingly fragmented, as the opportunities for cross-class interaction diminish. To reclaim the Third Place is not merely a nostalgic endeavor, but a political necessity for the restoration of a healthy and inclusive civic life.""",
    ),
    (
        "The Performance of Professionalism in the Digital Age",
        """In the modern corporate world, professionalism has evolved from a standard of competence into a sophisticated performance of availability and alignment with company values. The proliferation of digital communication tools, such as Slack and Microsoft Teams, has created an environment where presence is measured by the speed of one's response rather than the quality of one's output. The nuance of this digital etiquette lies in the unspoken expectation of perpetual connectivity, which effectively erodes the boundary between the professional and the private. Furthermore, the use of corporate jargon often serves to obfuscate power dynamics and sanitize the reality of labor. Consequently, employees find themselves navigating a complex semiotic landscape where the correct tone is as important as the technical skill. This performative culture, while ostensibly designed to foster efficiency, often results in a profound state of cognitive dissonance and emotional exhaustion.""",
    ),
    (
        "The Commodification of Attention and the Notification Economy",
        """In the late-stage capitalist economy, attention has become the most valuable commodity, leading to the rise of what scholars term the Notification Economy. Every digital interface is meticulously engineered to trigger dopamine responses, ensuring that the user remains engaged with the platform for as long as possible. The nuance of this system is its reliance on intermittent reinforcement-the same psychological mechanism that fuels gambling addiction. Consequently, the capacity for sustained, deep concentration is being systematically undermined by a barrage of superficial interruptions. Furthermore, the monetization of attention has led to a crisis of truth, as algorithms prioritize engagement over accuracy, facilitating the rapid spread of sensationalist disinformation. To protect one's attention is, therefore, a radical act of cognitive self-defense in a world designed to keep us perpetually distracted and reactive.""",
    ),
    (
        "The Myth of Meritocracy in the Modern Workplace",
        """The narrative of meritocracy-the idea that success is a direct result of individual talent and effort-remains the foundational myth of the modern workplace. However, a critical analysis reveals that this ideology often serves to legitimize existing inequalities and obscure the role of social capital and institutional bias. The nuance of the meritocratic trap is that those who succeed are encouraged to view their achievements as solely their own, leading to a lack of empathy for those who struggle against systemic barriers. Furthermore, the metrics used to measure merit are often skewed toward traits that are culturally and socially specific, effectively excluding diverse perspectives. Consequently, the pursuit of meritocracy can paradoxically reinforce the very hierarchies it claims to dismantle. Recognizing the role of luck and privilege is, therefore, essential for creating a truly equitable professional environment where opportunity is not a function of one's background.""",
    ),
    (
        "The Gentrification of Time: Speed as a Marker of Status",
        """In contemporary society, busyness has transitioned from a symptom of overwork into a prominent marker of social status. The faster one's life moves, the more valuable they are perceived to be within the market logic. This gentrification of time means that the luxury of slowness-of contemplative leisure and unhurried interaction-is increasingly reserved for those with significant economic security. The nuance of this phenomenon is its impact on the quality of human relationships; when time is viewed as a scarce resource to be optimized, conversations become transactional and empathy becomes an inefficiency. Furthermore, the constant drive for speed leads to a flattening of experience, where the depth of an encounter is sacrificed for the breadth of one's schedule. To resist the cult of speed is to insist on the inherent value of the present moment, independent of its productive utility.""",
    ),
    (
        "The Institutionalization of Self-Care",
        """While the self-care movement originated as a radical act of self-preservation for marginalized groups, it has increasingly been co-opted by corporate interests and rebranded as a personal responsibility for maintaining one's own productivity. In this institutionalized form, self-care is often reduced to the consumption of wellness products-scented candles, expensive memberships, or mindfulness apps-rather than a critique of the systemic causes of stress and burnout. The nuance of this shift is the individualization of the systemic; if you are stressed, the fault lies in your lack of resilience rather than in the exploitative nature of your workplace. Consequently, the burden of staying well is placed entirely on the individual, absolving the institution of its duty to provide a healthy environment. True self-care must involve a collective demand for better working conditions and a rejection of the idea that our worth is defined by our ability to endure exhaustion.""",
    ),
    (
        "The Semiotics of Urban Decay and Revitalization",
        """The lifecycle of urban neighborhoods is often narrated through the binary of decay and revitalization, yet these terms are frequently utilized to mask the displacement of vulnerable populations. What is labeled as urban decay is often the result of systematic disinvestment and political neglect, while revitalization (or gentrification) is driven by the influx of speculative capital. The nuance of this semiotic struggle lies in the aestheticization of the city; the industrial chic of a new cafe often signals the impending disappearance of the local laundromat or bodega. Consequently, the cultural history of the neighborhood is sanitized and packaged for a new, wealthier demographic. To understand urban change, one must move beyond the surface-level improvements and interrogate whose lives are being enhanced and whose are being erased in the name of progress.""",
    ),
    (
        "The Paradox of Digital Minimalism",
        """As the psychological toll of hyper-connectivity becomes increasingly apparent, the movement toward digital minimalism has gained significant traction. This philosophy advocates for the intentional reduction of digital tools to make space for more meaningful activities. However, the paradox of digital minimalism is that it is often facilitated by the very technology it seeks to limit; we use apps to track our screen time and digital platforms to discuss our offline lives. The nuance of this struggle is the realization that the digital and the analog are now inextricably linked. Consequently, unplugging is no longer a simple act of turning off a device, but a complex negotiation with a world that assumes constant availability. True digital minimalism requires a fundamental shift in our values, moving away from the logic of the more toward an appreciation for the enough, and recognizing that our worth is not a function of our digital engagement.""",
    ),
    (
        "The Bureaucracy of Empathy in Modern Institutions",
        """In large-scale modern institutions, from hospitals to corporate HR departments, empathy is increasingly being standardized and bureaucratized through the use of scripts and standard operating procedures. While the intention is to ensure a consistent level of service, the result is often a profound sense of inauthenticity. The nuance of this simulated empathy is that it prioritizes the appearance of care over the experience of care. Consequently, both the provider and the recipient find themselves trapped in a hollow performance that fails to address the underlying human need for genuine connection. Furthermore, when empathy is reduced to a metric to be measured, it loses its moral and emotional potency. To restore the human to our institutions, we must allow for the messiness and unpredictability of real interaction, recognizing that care cannot be automated or scripted without losing its essence.""",
    ),
    (
        "The Epistemology of the Life Hack",
        """The contemporary obsession with life hacks-small, clever techniques for increasing efficiency in daily tasks-reflects a deeper epistemological shift toward the optimization of the self. This perspective views the human body and mind as a series of systems to be hacked or improved through technological and psychological interventions. The nuance of this worldview is its inherent reductionism; it treats life as a collection of problems to be solved rather than an experience to be lived. Consequently, the quantified self movement, where individuals track every biological metric from sleep cycles to heart rate variability, can lead to a state of perpetual anxiety about one's own performance. Furthermore, the pursuit of total optimization often comes at the expense of spontaneity and joy. To live a full life is to accept the inefficiencies of our humanity-the detours, the mistakes, and the idle moments that cannot be hacked.""",
    ),
]


STORY_TEXTS["c2"] = [
    (
        "The Ontological Weight of the Threshold",
        """The domestic threshold, that seemingly innocuous boundary between the sanctity of the private dwelling and the chaotic exigencies of the public sphere, serves as a profound site of ontological transition. To cross a doorway is not merely a physical act of locomotion but a sophisticated reconfiguration of the self. In the sanctuary of the home, the individual is permitted a state of unmasked being, where the performative requirements of the social contract are temporarily suspended. However, as one approaches the threshold to engage with the world, there is a requisite donning of the persona-a psychological bracing for the gaze of the Other. The nuance of this transition lies in the liminality of the doorway itself; it is a space that belongs to neither realm, a vacuum of identity where we are briefly, and perhaps terrifyingly, nothing. To ignore the gravity of the threshold is to fail to understand the architecture of our own sanity. In the modern city, where digital connectivity threatens to dissolve all boundaries, the physical doorway remains a vital, albeit fragile, guardian of the private soul.""",
    ),
    (
        "The Melancholy of the Commute: A Study in Temporal Liminality",
        """The daily commute, often dismissed as a sterile interval of non-productivity, is in fact a sophisticated exercise in temporal liminality. It is a period where the individual is suspended between the roles of dweller and worker, inhabiting a transient space that defies traditional categorization. In the rhythmic oscillation of the subway or the stagnant flow of traffic, we encounter a unique form of modern melancholy-a realization of the fungibility of our time. The nuance of this experience is the anonymity of the crowd; surrounded by hundreds of others engaged in the same ritual, one is forced to confront the absolute insignificance of their own trajectory within the urban machine. Consequently, the commute becomes a site of involuntary meditation, where the mind, stripped of its usual distractions, is often visited by the existential shudder. To survive the commute is to negotiate a peace treaty with the void, recognizing that these lost hours are, paradoxically, some of the most authentically human moments of our day, precisely because they serve no purpose other than the transition itself.""",
    ),
    (
        "The Semiotics of the Grocery List: A Fragmented Autobiography",
        """The humble grocery list, a document usually destined for the recycling bin, functions as a remarkably dense fragmented autobiography. It is a testament to our biological necessities, our fleeting desires, and our aspirations for a better, healthier version of ourselves. The nuance of the list lies in the tension between the ideal self-represented by the kale and the quinoa-and the visceral self, found in the late-night chocolate and the processed comforts. It is a map of our domestic priorities and a record of our economic constraints. Furthermore, the act of crossing out an item provides a minor, yet essential, sense of agency in an increasingly chaotic world. When we analyze a list found in a discarded cart, we are not merely looking at a tally of commodities; we are peering into the domestic rituals of a stranger. The grocery list proves that the most profound truths about our existence are often written in the margins of the mundane, encoded in the syntax of milk, bread, and forgotten intentions.""",
    ),
    (
        "The Aesthetics of the Banal: On the Poetics of the Laundromat",
        """There is a specific, almost transcendent, beauty to be found in the aesthetics of the banal, particularly within the clinical, fluorescent-lit confines of a public laundromat. It is a space of radical democracy, where the intimate garments of disparate lives tumble together in a rhythmic, mechanical dance. The nuance of the laundromat is its temporal suspension; the time it takes for a cycle to complete is a period of enforced stillness, a reprieve from the frantic acceleration of the Notification Economy. In the hum of the dryers and the scent of synthetic lavender, one encounters a form of secular monastery. The mundane act of folding clothes becomes a ritual of restoration-an attempt to bring order to the entropic decay of the physical world. To appreciate the laundromat is to recognize that the sacred is not something found in the extraordinary, but something that emerges through the patient, repetitive care we provide to the basic requirements of our biological life.""",
    ),
    (
        "The Epistemology of the Inbox Zero",
        """The modern quest for Inbox Zero-the state of having an empty email inbox-is more than a strategy for productivity; it is a profound epistemological desire for a finished world. In the digital age, where information is an infinite, entropic tide, the empty inbox represents a temporary victory over the chaos of the Always-On culture. The nuance of this obsession is the realization that an empty inbox is a phantom; it is a state that exists only for the millisecond before the next notification arrives. Consequently, the pursuit of Inbox Zero is a Sisyphean labor, a repetitive attempt to achieve a clarity that the medium itself is designed to prevent. This reflects a deeper anxiety about our own finitude; we believe that if we can clear the deck of our digital obligations, we will finally have the time to begin our true lives. The irony, of course, is that the clearing of the deck is the life itself. To find peace in the digital age is to accept the permanent state of the unfinished and to learn to live within the flow rather than trying to dam the river.""",
    ),
    (
        "The Architecture of Solitude in the Crowded Metropolis",
        """Solitude in the modern metropolis is not the absence of others, but the cultivation of an interior distance. It is a sophisticated psychological architecture that allows the individual to remain sovereign within the crushing proximity of the mass. The nuance of urban solitude is found in the public-private rituals of the coffee shop or the park bench, where one is alone together with a multitude of strangers. This state of monastic urbanism requires a deliberate filtering of the sensory environment-a selective blindness and a strategic deafness that protects the integrity of the self. Consequently, the city becomes a labyrinth of invisible cells, each inhabited by an individual engaged in their own private narrative. This is not a failure of community, but a necessary adaptation for the preservation of the psyche. To master urban solitude is to recognize that the most expansive landscapes are not found in the wilderness, but within the silent intervals of a crowded afternoon.""",
    ),
    (
        "The Phenomenology of the Broken Appliance",
        """The sudden failure of a domestic appliance-a refrigerator that ceases to cool or a kettle that refuses to boil-triggers a profound phenomenological rupture. Ordinarily, these objects are invisible in their functionality; we interact with them through a pre-reflexive habit. However, when they break, they transition from tools into obstacles, forcing us to confront the fragile infrastructure of our daily comfort. The nuance of this encounter is the realization of our technological dependency. We find ourselves standing before a silent machine, feeling a sense of betrayal that is almost personal. This rupture exposes the hauntology of the domestic-the way our lives are haunted by the potential failure of the systems we take for granted. To repair a broken appliance is to perform a minor act of cosmic restoration, a re-establishment of the harmony between the human intention and the material world. It is a reminder that our civilization is a thin veneer of functionality stretched over a vast, entropic silence.""",
    ),
    (
        "The Semiotics of the Elevator: A Ritual of Vertical Liminality",
        """The elevator is a site of intense, albeit brief, vertical liminality, a space where the social contract is tested by the absolute proximity of strangers. Within the steel confines of the lift, the usual rules of eye contact and personal distance are suspended in favor of a rigid, collective silence. The nuance of the elevator ritual is the asceticism of the gaze; we look at the floor, the ceiling, or the changing numbers, doing anything to avoid acknowledging the visceral presence of the Other. This shared performance of civil inattention is what allows the high-rise city to function. Furthermore, the elevator represents a transition between different spheres of authority and identity-from the street to the office, or from the lobby to the home. To inhabit an elevator is to exist in a state of suspended animation, a vertical journey that mirrors the precariousness of our own social and physical positions in the urban hierarchy.""",
    ),
    (
        "The Ethics of the Wait: On the Virtue of the Queue",
        """The queue, that most maligned of social structures, is in fact a profound monument to the democratic ideal. It is a physical manifestation of the principle of equality-a declaration that one's time is no more valuable than that of the person ahead. The nuance of the wait lies in its rejection of the ego; to stand in line is to accept the sovereignty of the collective order over one's individual desire for speed. In an age characterized by the logic of the instant, the queue serves as a necessary, albeit frustrating, brake on the acceleration of the self. Furthermore, the wait provides a unique opportunity for idle observation-a chance to witness the minor dramas and subtle etiquettes of our fellow citizens. To embrace the wait is to practice a form of secular patience, recognizing that the shortest path is not always the most meaningful one. The queue reminds us that we are not merely consumers in a market, but citizens in a shared, and sometimes slow, reality.""",
    ),
    (
        "The Alchemical Transmutation of the Daily Grind",
        """The daily grind-that repetitive cycle of labor and maintenance-is often viewed as the primary enemy of a meaningful life. However, from a C2-level perspective, the grind is the very materia prima of existence. It is the raw material through which we forge our character and our resilience. The nuance of this alchemical process is the transmutation of the mundane into the sacred. By performing our daily tasks with a sense of radical presence, we transform the chore into a ritual and the job into a vocation. This is not a romanticization of labor, but a recognition of the poetics of persistence. The grind provides the necessary friction that allows the soul to develop its texture. To find joy in the repetition of the days is to achieve the ultimate human victory-to realize that the extraordinary is not a destination we reach, but a quality of attention we bring to the most ordinary moments of our lives.""",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, rotina, comandos e vocabulario de sobrevivencia",
    "a1": "rotina, frequencia, planos para o futuro e interacao social",
    "a2": "passado simples e continuo, experiencias, comparativos e problemas diarios",
    "b1": "opinioes, conselhos, causa e consequencia, verbos modais e conectores logicos",
    "b2": "analise sociocultural, vida profissional e vocabulario abstrato",
    "c1": "analise institucional, critica de sistemas e registro formal academico",
    "c2": "registro erudito, ensaio fenomenologico e densidade literaria",
}


class Command(BaseCommand):
    help = "Replace the Cotidiano catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="cotidiano")
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
                text.slug = slugify(f"{level.slug}-cotidiano-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Cotidiano texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre cotidiano: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D educational everyday-life storybook style, clean lines, high quality, "
            f"scene about {title}, showing {scene}, featuring the book-mascot Alexandrinho, "
            "using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
