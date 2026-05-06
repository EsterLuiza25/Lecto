import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


HEALTH_TEXTS = {
    "iniciante": [
        (
            "The Glass of Water",
            "Water is very good for the body. I have a glass of water on the table. The water is cold and fresh. I drink water in the morning. I drink water in the afternoon. My body is happy when I drink water. It is a simple habit. Water is life. I drink eight glasses every day.",
        ),
        (
            "An Apple a Day",
            "This is a red apple. The apple is sweet and crunchy. Fruit is healthy food. I eat an apple for snack. My friend eats a banana. We like fruit because it has vitamins. The apple is on the plate. Eating fruit is a good choice for my health. I feel strong today.",
        ),
        (
            "Time to Sleep",
            "The night is quiet. I am in my bed. The bed is soft and warm. It is time to sleep. I sleep for eight hours. Sleep is important for the brain. I close my eyes and rest. In the morning, I have a lot of energy. A good sleep makes a happy day.",
        ),
        (
            "Walking in the Morning",
            "The sun is bright. I walk in the park every morning. I wear comfortable shoes. Walking is a simple exercise. I see the green trees. I breathe the fresh air. My legs are strong. My heart is healthy. I walk for twenty minutes. It is a great start for my day.",
        ),
        (
            "Washing My Hands",
            "I am in the bathroom. I have soap and water. I wash my hands before dinner. I wash my hands after the park. My hands are clean and fresh. Clean hands are important for health. I use a white towel. It is a very easy habit. I stay healthy when I am clean.",
        ),
        (
            "A Big Green Salad",
            "The salad is in a big bowl. There is green lettuce and red tomatoes. I like vegetables. Vegetables are very healthy. I put a little olive oil on the salad. The food is colorful and delicious. My family eats salad every day. Healthy food makes a healthy body. I like my green salad.",
        ),
        (
            "My Strong Muscles",
            "I go to the gym. I lift small weights. My muscles are getting strong. Exercise is good for the body. I wear a blue t-shirt and shorts. I drink water during my exercise. I feel tired but I am happy. Moving the body is very important. I am a healthy person.",
        ),
        (
            "A Happy Smile",
            "I brush my teeth in the morning. I brush my teeth at night. I use a toothbrush and toothpaste. My teeth are white and clean. A healthy mouth is important. I go to the dentist every year. I have a big, happy smile. Taking care of my teeth is a good habit.",
        ),
        (
            "Fresh Air and Sunshine",
            "I open the window of my room. I feel the fresh air. I see the yellow sun. Sunshine is good for the body. It gives me Vitamin D. I sit near the window for ten minutes. The air is clean. The sun is warm. I feel calm and relaxed. Nature is a natural medicine.",
        ),
        (
            "Stretching My Body",
            "I stand up from my chair. I stretch my arms up high. I touch my toes with my hands. Stretching is good for the back. My body feels flexible and light. I do this every afternoon at work. It is a short break for my muscles. I feel better after I stretch my body.",
        ),
    ],
    "a1": [
        (
            "My Morning Routine",
            "Every morning, I wake up at seven o'clock and I drink a large glass of water. This is important because it helps my body wake up. After that, I eat a healthy breakfast with oats, yogurt, and some fresh blueberries. I don't drink coffee because it makes me feel nervous, so I prefer green tea. Before I start my work, I do ten minutes of yoga in my living room. This routine helps me stay calm and focused during the day. I think that a good start in the morning is the secret to a healthy life.",
        ),
        (
            "Why We Need Vegetables",
            "Vegetables are an essential part of a healthy diet because they contain many vitamins and minerals. My doctor says I need to eat different colors of vegetables every day. For example, carrots are good for the eyes and spinach makes the muscles strong. I usually prepare a big salad for lunch and I add some olive oil and lemon. Sometimes I don't like the taste of broccoli, but I eat it because it is very good for my heart. Eating vegetables gives me energy to study and play sports with my friends.",
        ),
        (
            "The Importance of Daily Exercise",
            "Exercise is not only for athletes; it is for everyone who wants to be healthy. I try to be active every day because it makes my heart strong and my mind happy. In the afternoon, I usually go for a fast walk in the park or I ride my bicycle for thirty minutes. Sometimes I go to the gym with my friend Geovanna, and we exercise together. It is difficult to start when I am tired, but I always feel much better after the workout. Regular exercise is a great way to reduce stress.",
        ),
        (
            "Taking Care of My Mental Health",
            "Health is not just about the body; the mind is also very important. When I feel stressed about my university exams, I take a short break. I sit in a quiet place, close my eyes, and breathe deeply for five minutes. This simple meditation helps me relax and clear my head. I also like to write my thoughts in a journal before I go to sleep. Talking to friends and family is another good way to take care of my mental health. Being happy and calm is part of a healthy lifestyle.",
        ),
        (
            "Sleeping Well for a Better Brain",
            "A good night's sleep is necessary for a healthy brain. Doctors recommend sleeping between seven and nine hours every night. When I don't sleep well, I feel tired and I cannot concentrate on my software engineering projects. To sleep better, I turn off my phone and the television one hour before bed. I like to read a book because it relaxes my eyes. A dark and quiet room is perfect for a deep sleep. In the morning, I wake up with a lot of energy and a positive attitude.",
        ),
        (
            "The Sugar Problem",
            "Many people love sweet things like soda, chocolate, and cake, but too much sugar is bad for the health. Sugar gives you energy for a short time, but then you feel very tired. It is also bad for your teeth and can cause many diseases. I try to drink water or natural fruit juice instead of soda because it is more natural. When I want something sweet, I eat a piece of dark chocolate or some sweet fruit. Small changes in our food can make a big difference in how we feel every day.",
        ),
        (
            "Staying Hydrated",
            "Our bodies are made of a lot of water, so we need to drink fluids all day long. Drinking water is the best way to stay hydrated. I always carry a reusable water bottle in my backpack when I go to the university. Sometimes I add a slice of lemon or some mint to my water because it tastes fresh. When I am hydrated, my skin looks better and I don't have headaches. It is a very simple habit, but it is one of the most important things for a healthy body.",
        ),
        (
            "A Visit to the Doctor",
            "Going to the doctor for a check-up is a responsible habit. Even when I feel good, I visit my doctor once a year to check my blood and my heart. The doctor asks me questions about my food and my exercise routine. Sometimes I need to take vitamins because my body needs more energy. I am not afraid of the doctor because she helps me stay healthy and prevents problems in the future. It is better to prevent a disease than to treat it later. Taking care of myself is my priority.",
        ),
        (
            "The Benefits of Sun Exposure",
            "Sunshine is very good for our health because it helps our body produce Vitamin D. This vitamin is important for strong bones and a good immune system. Every afternoon, I try to spend fifteen minutes in the sun. I usually sit in my garden or walk to the supermarket. However, I must be careful because too much sun can burn the skin. When I stay outside for a long time, I always use sunscreen and wear a hat. A little bit of sun every day makes me feel more energetic and happy.",
        ),
        (
            "Healthy Snacks for Students",
            "As a student, I am often hungry between classes, but I try to avoid fast food. I pack some healthy snacks in my bag every morning. My favorite snacks are nuts, like almonds and walnuts, because they are good for memory. I also like to bring an apple or a pear. These snacks are better than chips or cookies because they don't have too much salt or fat. Eating small, healthy meals during the day helps me stay focused on my coding tasks and prevents me from feeling too hungry at dinner.",
        ),
    ],
    "a2": [
        (
            "Changing My Diet for Good",
            "Last year, I realized that I was eating too much fast food and processed snacks. I felt tired every afternoon and my skin was not very clear. Because of this, I decided to change my eating habits in January. I stopped drinking soda and started drinking more water and natural juices. At first, it was more difficult than I expected because I missed sugar. However, after one month, I felt much more energetic and focused. Now, I prefer eating home-cooked meals with fresh vegetables because they are tastier and healthier than restaurant food. I also lost some weight and my sleep is better now. Making these changes was the best decision I made for my body. Today, I am much happier with my lifestyle than I was a year ago.",
        ),
        (
            "My First 5K Race",
            "Two months ago, I participated in a 5K race in Brasilia. Before that day, I was not a very active person and I didn't like running at all. I started training in the park three times a week with my friend Clara. In the beginning, running for ten minutes was harder for me than studying for a difficult exam! But slowly, my legs became stronger and my breathing was more controlled. On the day of the race, I was very nervous, but the atmosphere was amazing. I ran faster than I did during my practice sessions. When I crossed the finish line, I felt incredibly proud of myself. Running a 5K was a big challenge, but it proved that I can improve my physical health with persistence.",
        ),
        (
            "The Benefits of Group Classes",
            "I used to exercise alone at home, but last month I joined a functional training class at a local gym. I discovered that exercising with other people is much more motivating than working out by myself. In the group class, the instructor shows us the correct way to do every movement, which is safer for my back and knees. Also, the music is louder and the energy is higher than in my living room. I met new friends and we help each other during the difficult exercises. Although the classes are more expensive than a free app, the results are better because I don't skip my workouts anymore. Now, I look forward to my classes every Tuesday and Thursday.",
        ),
        (
            "A Lesson in Stress Management",
            "Last semester at the university was very stressful because I had many coding projects and exams at the same time. I started having headaches and I couldn't sleep well at night. My professor suggested that I try a meditation app to help me relax. I started using it for ten minutes every night before bed. It was simpler than I thought! The app taught me how to focus on my breath and let go of my worries. After two weeks, my stress levels were lower and my mind was clearer. I realized that taking care of my mental health is as important as taking care of my physical health. Now, I am more relaxed even when I have a lot of work to do.",
        ),
        (
            "Comparing Yoga and Weightlifting",
            "Recently, I tried two very different types of exercise: yoga and weightlifting. I went to a yoga studio on Monday and a traditional gym on Wednesday. Yoga was much more relaxing and focused on flexibility, while weightlifting was more intense and focused on building muscle. I found that yoga is better for my posture and for reducing anxiety. On the other hand, weightlifting made me feel stronger and more powerful. I liked both, but for different reasons. My friend Geovanna prefers yoga because it is quieter, but I think a combination of both is the best for a balanced body. It is interesting to see how different activities can help our health in various ways.",
        ),
        (
            "Recovering from a Small Injury",
            "Last summer, I hurt my ankle while I was playing soccer with my classmates. It was a painful experience, and I had to stop exercising for three weeks. My doctor said that resting was the most important thing for my recovery. I stayed home and used ice on my ankle every day. It was very boring because I am an active person, but I understood that my body needed time to heal. When I started walking again, I was more careful than before. I also started doing special stretches to make my ankle stronger. This injury taught me that we must listen to our bodies and respect our limits to stay healthy in the long term.",
        ),
        (
            "Traditional Medicine vs. Modern Habits",
            "When I was a child, my grandmother always made herbal teas when I was sick. She believed that natural ingredients like ginger and honey were better for a cold than chemical medicine. Last week, I had a sore throat, so I decided to try her recipe instead of buying pills at the pharmacy. Surprisingly, I felt better very quickly! The warm tea was more soothing for my throat than any medicine I used in the past. Of course, modern medicine is essential for serious problems, but I think traditional home remedies are great for small issues. It is important to find a balance between natural wisdom and modern science to maintain our well-being.",
        ),
        (
            "The Importance of Ergonomics",
            "Since I started my internship in operations management, I spend many hours sitting in front of a computer. Last month, my back started to hurt every day. I realized that my chair was not very comfortable and my monitor was too low. I decided to learn about ergonomics to fix my workspace. I bought a better chair and I adjusted the height of my screen. I also started taking short breaks to stretch every hour. The difference was immediate! My back feels much better now and I am more productive at work. Good posture is more important than people think, especially for students and office workers.",
        ),
        (
            "Discovering the Power of Breakfast",
            "In the past, I never ate breakfast because I was always in a hurry to get to my classes. I usually just drank a cup of coffee and left the house. However, I often felt tired and hungry by ten o'clock. Last month, I decided to wake up fifteen minutes earlier to eat a real breakfast with eggs, fruit, and whole-grain bread. The change was incredible! I have more energy for my morning lectures and I can concentrate better on my studies. Breakfast is definitely the most important meal of the day. Now, I never leave home without eating something healthy and nutritious.",
        ),
        (
            "A Weekend Without Technology",
            "Two weeks ago, I decided to do a digital detox for the whole weekend. I turned off my smartphone, my laptop, and the television. At first, I felt a bit anxious because I wanted to check my messages. But after a few hours, I felt much calmer and more present. I spent my time reading a physical book, cooking a healthy meal, and walking in nature. My brain felt more relaxed than when I am constantly scrolling through social media. I slept better on Sunday night and I felt more creative on Monday morning. I think everyone should try a technology-free weekend once a month for their mental well-being.",
        ),
    ],
    "b1": [
        (
            "The Hidden Dangers of a Sedentary Lifestyle",
            "In the modern era, many people spend the majority of their day sitting down, whether they are studying at a university or working in an office. This is known as a sedentary lifestyle, and it has serious consequences for long-term health. Because the human body was designed for movement, staying still for many hours leads to poor circulation and weakened muscles. Consequently, sedentary individuals have a higher risk of developing heart disease and back pain. Furthermore, a lack of physical activity can negatively affect your mental health, causing feelings of lethargy and low motivation. In my opinion, we must find ways to integrate movement into our daily routines. For example, taking the stairs instead of the elevator or using a standing desk can make a significant difference. Although it requires effort to break the habit of sitting, the benefits for your energy levels and physical longevity are undeniable. Therefore, we should prioritize small active breaks every hour to protect our well-being.",
        ),
        (
            "The Relationship Between Nutrition and Mental Clarity",
            "Most people understand that food affects physical weight, but few realize the profound connection between nutrition and mental clarity. Our brains require a constant supply of high-quality fuel to function efficiently. Consequently, a diet high in processed sugars and unhealthy fats can lead to brain fog, making it difficult to concentrate on complex tasks like software engineering. On the other hand, consuming brain foods such as fatty fish, nuts, and leafy greens provides the essential nutrients needed for cognitive performance. Furthermore, staying hydrated is crucial because even mild dehydration can cause irritability and fatigue. In my view, we should treat our diet as an investment in our intellectual capacity. If you eat balanced meals, you will likely notice an improvement in your memory and your ability to solve problems under pressure. Therefore, paying attention to what you eat is not just about vanity; it is a fundamental strategy for academic and professional success.",
        ),
        (
            "The Importance of Work-Life Balance",
            "Achieving a healthy work-life balance is one of the greatest challenges for young professionals and interns today. Because of the high pressure to succeed, many individuals work long hours and ignore their personal needs. This often leads to burnout, a state of emotional and physical exhaustion that can take months to recover from. Furthermore, when you neglect your social life and hobbies, your overall happiness decreases, which ironically makes you less productive at work. In my opinion, setting clear boundaries is essential for a sustainable career. For instance, you should avoid checking work emails during your free time and ensure you have enough hours for rest and exercise. Consequently, you will feel more refreshed and motivated when you return to your professional tasks. In conclusion, being successful is not only about how much you work, but about how well you manage your energy and your time for yourself.",
        ),
        (
            "Why Sleep Hygiene is Essential",
            "Many people view sleep as a luxury that can be sacrificed for more study or work time. However, sleep hygiene is actually a biological necessity that affects every system in the body. During deep sleep, the brain processes information and clears out toxins. Consequently, chronic sleep deprivation leads to impaired judgment, a weakened immune system, and increased stress levels. To improve sleep quality, it is important to establish a consistent routine, such as going to bed at the same time every night. Furthermore, you should avoid blue light from smartphones before bed because it interferes with the production of melatonin, the sleep hormone. In my view, we need to stop glorifying all-nighters and start respecting the power of rest. A well-rested mind is much more creative and resilient than one that is constantly exhausted. Therefore, investing in a good night's sleep is the most effective way to improve your health and your performance during the day.",
        ),
        (
            "The Impact of Social Media on Self-Esteem",
            "Social media has revolutionized communication, but it has also created new challenges for our mental well-being and self-esteem. Because platforms like Instagram often show a curated and idealized version of reality, many users begin to compare their real lives with these digital illusions. Consequently, this constant comparison can lead to feelings of inadequacy, anxiety, and even depression. Furthermore, the like system creates a dependency on external validation, which can be very damaging to one's self-worth. In my opinion, it is vital to practice digital mindfulness by being conscious of who we follow and how much time we spend online. If a specific account makes you feel bad about yourself, you should unfollow it immediately. In conclusion, while technology is a great tool, we must ensure that it doesn't dictate our happiness or our perception of our own value.",
        ),
        (
            "The Benefits of Mindful Eating",
            "Mindful eating is a practice that involves paying full attention to the experience of eating, rather than consuming food while distracted by a screen or work. This is important because when we eat too fast, our brain doesn't have time to receive the signal that we are full. Consequently, mindless eating often leads to overeating and poor digestion. Furthermore, by focusing on the flavors, textures, and smells of our food, we derive more satisfaction from smaller portions. In my view, this approach helps us develop a healthier relationship with food, moving away from restrictive diets and toward intuitive choices. Although it can be difficult to find the time to eat slowly in a busy schedule, the benefits for our metabolism and our enjoyment of life are significant. Therefore, try to put away your phone during lunch and focus entirely on your meal to improve your overall well-being.",
        ),
        (
            "How Chronic Stress Affects the Immune System",
            "Stress is often considered a purely psychological issue, but it has very real physical consequences, particularly for the immune system. When we are constantly stressed, our bodies produce high levels of cortisol, a hormone that suppresses the immune response. Consequently, people who experience chronic stress are more likely to get sick and take longer to recover from infections. Furthermore, stress often leads to other unhealthy habits, such as poor diet and lack of sleep, which further weaken our defenses. In my opinion, learning stress-management techniques, such as deep breathing or regular exercise, is essential for physical health. By reducing our internal tension, we allow our immune system to function at its full capacity. Therefore, managing your stress is not just about feeling calm; it is a vital part of preventing physical illness and staying strong.",
        ),
        (
            "The Role of Community in Personal Well-being",
            "Humans are social creatures, and the strength of our community connections plays a major role in our personal well-being. Research shows that people with strong social ties are generally happier and live longer than those who are isolated. This happens because having a support system provides emotional security and reduces the impact of life's challenges. Furthermore, being part of a group-whether it's a sports team, a coding club, or a family-gives us a sense of purpose and belonging. Consequently, social isolation can be as damaging to health as smoking or obesity. In my view, we should make an active effort to nurture our relationships and participate in community events. Even as our lives become more digital, the need for real-world connection remains fundamental. Therefore, investing time in your friends and family is just as important as investing in your career or your physical fitness.",
        ),
        (
            "The Future of Telemedicine and Digital Health",
            "The rise of telemedicine has made healthcare more accessible and convenient than ever before. Because of digital platforms, patients can now consult with doctors from the comfort of their homes, which is especially beneficial for those living in remote areas. Furthermore, wearable technology like smartwatches allows us to monitor our heart rate, sleep patterns, and activity levels in real-time. Consequently, we are becoming more proactive about our health, catching potential problems before they become serious. However, some argue that digital health can lead to cyberchondria, where people become overly anxious after researching symptoms online. In my opinion, while technology is a powerful ally, it should supplement, not replace, the human connection in medicine. Therefore, we should embrace these digital tools while maintaining a critical mind and trusting professional medical advice.",
        ),
        (
            "Why We Should Prioritize Functional Fitness",
            "Functional fitness is a type of exercise that focuses on preparing the body for real-life movements and activities, rather than just building big muscles for appearance. This approach includes exercises that improve balance, coordination, and core strength, such as squats and lunges. This is important because as we age, functional strength prevents injuries and allows us to remain independent. Furthermore, it makes daily tasks, like carrying heavy groceries or sitting at a desk for long periods, much easier on the body. Consequently, many people find that functional training is more practical and rewarding than traditional bodybuilding. In my view, the goal of exercise should be to enhance the quality of our daily lives. If you can move through your day with ease and without pain, you have achieved true physical fitness. Therefore, consider adding functional movements to your routine to build a body that is both strong and useful.",
        ),
    ],
}


HEALTH_TEXTS["b2"] = [
    (
        "The Gut-Brain Axis: Understanding the Second Brain",
        "Recent scientific breakthroughs have revealed a fascinating and complex connection between our digestive system and our mental health, commonly referred to as the gut-brain axis. It is now understood that the gut is home to trillions of bacteria, known as the microbiome, which communicate directly with the central nervous system. Consequently, an imbalance in these bacteria-often caused by a diet of highly processed foods-can be linked to conditions such as anxiety and depression. Furthermore, roughly 95% of the body's serotonin, a hormone responsible for mood regulation, is produced in the gut. In my opinion, this discovery should fundamentally change how we approach mental health treatment. Instead of focusing solely on neurological interventions, we must also consider nutritional psychiatry as a viable path to emotional stability. If we nourish our second brain with fiber-rich and fermented foods, we are essentially fortifying our minds against psychological distress.",
    ),
    (
        "The Rise of Biohacking: Optimizing the Human Machine",
        "Biohacking, the practice of using science and technology to upgrade one's body and mind, has transitioned from a niche subculture to a mainstream health trend. From intermittent fasting and cold exposure to the use of nootropics for cognitive enhancement, biohackers seek to optimize human performance beyond traditional medical advice. Proponents argue that by monitoring biomarkers in real-time, individuals can take full control of their biological destiny. However, this trend raises significant ethical and safety concerns, as some interventions lack rigorous clinical validation. Furthermore, the obsession with optimization can paradoxically lead to increased stress and orthorexia-an unhealthy fixation on eating only pure foods. In my view, while the proactive spirit of biohacking is commendable, it must be balanced with common sense and professional guidance. We should strive for longevity, but not at the expense of our psychological well-being or social spontaneity.",
    ),
    (
        "Antibiotic Resistance: A Silent Global Crisis",
        "One of the most pressing threats to modern medicine is the rapid emergence of antibiotic-resistant superbugs. This crisis has been primarily driven by the over-prescription of antibiotics in healthcare and their excessive use in industrial livestock farming. Consequently, common infections that were once easily treated are becoming potentially life-threatening once again. If this trend continues at its current pace, we may enter a post-antibiotic era where routine surgeries and minor injuries pose significant risks. Furthermore, the development of new antibiotics has slowed down significantly because they are less profitable for pharmaceutical companies than chronic disease medications. In my opinion, addressing this issue requires a global, multi-faceted approach, including stricter regulations on antibiotic sales and increased public awareness about viral versus bacterial infections. We must protect these miracle drugs before they lose their efficacy entirely, as the stability of our global health infrastructure depends on them.",
    ),
    (
        "The Psychology of Habit Formation and Breaking",
        "Understanding the neurological mechanics of habit formation is essential for anyone seeking to improve their lifestyle. Habits operate in a loop consisting of a cue, a routine, and a reward. Because these loops are stored in the basal ganglia-a primitive part of the brain-they are notoriously difficult to overwrite once established. To successfully break a negative habit, one must identify the specific cue that triggers the behavior and find a healthier routine that delivers a similar reward. For example, if stress at work, the cue, leads to snacking on junk food, the routine, one might substitute the snack with a five-minute walk to achieve the same stress-relief, the reward. Furthermore, consistency is more important than intensity; it takes an average of 66 days for a new behavior to become automatic. In my view, self-discipline is a finite resource, so designing an environment that minimizes temptations is much more effective than relying on willpower alone.",
    ),
    (
        "The Ethics of Genetic Engineering and Longevity Research",
        "Advances in CRISPR technology and longevity research have brought us to the threshold of a new era where we might be able to edit our genetic code to prevent diseases or even slow down the aging process. While the potential to eradicate hereditary conditions is undeniably exciting, it presents profound ethical dilemmas. If these genetic upgrades become available only to the wealthy, we risk creating a biological divide in society, where longevity is a luxury rather than a right. Furthermore, we must consider the long-term ecological and demographic consequences of significantly extending the human lifespan. Would our planet be able to sustain a population that lives for 150 years? In my opinion, while scientific progress should not be stifled, it must be governed by a rigorous international ethical framework. We need to ensure that biotechnology is used to diminish suffering rather than to create new forms of inequality.",
    ),
    (
        "Environmental Toxins and the Endocrine System",
        "We are living in a world saturated with synthetic chemicals, many of which act as endocrine disruptors in the human body. These substances, found in everything from plastic containers to pesticides and cosmetics, mimic natural hormones and interfere with the body's delicate signaling systems. Consequently, exposure to these toxins has been linked to rising rates of hormonal imbalances, infertility, and metabolic disorders. Furthermore, children and pregnant women are particularly vulnerable to these disruptions, which can have lifelong impacts on development. In my view, the current regulatory innocent until proven guilty approach to chemical safety is inadequate. We must advocate for more transparent labeling and stricter bans on known harmful substances like BPA and phthalates. Protecting our endocrine health requires not only individual awareness-such as choosing glass over plastic-but also collective political action to demand a cleaner and safer environment for all.",
    ),
    (
        "The Blue Zones: Lessons from the World's Longest-Lived People",
        "Research into the Blue Zones-geographic regions where people live significantly longer and healthier lives-has provided invaluable insights into the secrets of longevity. Whether in Okinawa, Japan, or Sardinia, Italy, these populations share several key lifestyle traits: a primarily plant-based diet, regular moderate physical activity integrated into daily life, and a strong sense of community and purpose. Furthermore, these individuals often have low levels of chronic stress due to their traditional social structures and slow pace of life. Interestingly, their longevity is rarely a result of intense gym sessions or expensive supplements, but rather of a natural environment that encourages healthy movement and social connection. In my opinion, modern society has much to learn from these cultures. Instead of looking for a magic pill for health, we should focus on rebuilding our social support systems and simplifying our diets. Longevity is not a destination, but a byproduct of a life lived in balance with nature and community.",
    ),
    (
        "Sleep Apnea: The Underdiagnosed Sleep Disorder",
        "Sleep apnea is a serious sleep disorder characterized by repeated interruptions in breathing during the night, yet it remains significantly underdiagnosed in the general population. Because the symptoms-such as loud snoring and daytime fatigue-are often dismissed as common nuisances, many individuals suffer for years without seeking medical help. However, the consequences of untreated sleep apnea are severe, including an increased risk of hypertension, stroke, and type 2 diabetes. Furthermore, the resulting sleep fragmentation impairs cognitive function and significantly increases the likelihood of accidents at work or while driving. In my view, screening for sleep disorders should be a routine part of primary healthcare. If we improve awareness about the importance of airway health and the availability of treatments like CPAP machines, we can dramatically improve the quality of life and long-term health outcomes for millions of people.",
    ),
    (
        "The Impact of Ultra-Processed Foods on Global Health",
        "The global shift toward Westernized diets, dominated by ultra-processed foods, or UPFs, is arguably the primary driver of the current obesity and diabetes pandemic. UPFs are industrially manufactured substances that often contain high levels of additives, unhealthy fats, and refined sugars, while being devoid of fiber and essential nutrients. Because these foods are engineered to be hyper-palatable, they override our natural hunger signals and encourage overconsumption. Furthermore, they are often cheaper and more convenient than fresh ingredients, making them the default choice for low-income populations. In my opinion, the food industry must be held accountable for the health impacts of their products. Implementing sugar taxes and restricting the marketing of UPFs to children are necessary steps toward public health. We cannot expect individuals to fight a biological battle against scientifically engineered food without strong systemic support and better nutritional education.",
    ),
    (
        "Digital Health and the Quantified Self",
        "The Quantified Self movement, which involves the use of wearable technology and apps to track every aspect of one's physiology, has revolutionized personal health management. By monitoring heart rate variability, sleep stages, and even blood glucose levels, individuals can gain an unprecedented understanding of how their daily choices affect their bodies. Consequently, this data-driven approach allows for personalized interventions that are far more effective than one-size-fits-all medical advice. However, there is a risk that this constant monitoring can lead to health anxiety and a disconnected relationship with one's own body, where we trust the data more than our own sensations. In my view, digital health tools are most effective when used as a compass rather than a map. We should use them to gain insights, but we must also remain intuitive and mindful of our internal signals. The goal of health technology should be to empower the individual, not to turn life into a series of stressful metrics.",
    ),
]


HEALTH_TEXTS["c1"] = [
    (
        "The Medicalization of the Human Condition",
        "The contemporary era is characterized by an unprecedented trend toward the medicalization of the human condition, a process wherein experiences once considered part of the normal spectrum of existence are reclassified as pathological conditions requiring clinical intervention. This shift is particularly evident in the realm of mental health, where the nuances of grief, shyness, and existential malaise are increasingly viewed through a pharmacological lens. While the destigmatization of mental illness is undoubtedly a positive development, the propensity to pathologize every emotional fluctuation risks stripping individuals of their resilience and the capacity for self-reflection. The nuance of this debate lies in the tension between genuine therapeutic need and the profit-driven expansion of the pharmaceutical industry. We must interrogate whether we are fostering a more compassionate society or merely creating a culture of dependency where the pill for every ill becomes the default response to the inherent complexities of life.",
    ),
    (
        "Bioethics and the Sovereignty of the Patient",
        "As medical technology advances at a dizzying pace, the foundational principles of bioethics-autonomy, beneficence, and justice-are being subjected to rigorous re-examination. The sovereignty of the patient, once a straightforward concept, has become complicated by the emergence of life-extending technologies that challenge our definitions of dignity and natural death. The nuance here involves the delicate balance between the duty to preserve life and the right to refuse treatment in the face of irreversible suffering. This ethical landscape is further convoluted by the global disparity in healthcare access, where the autonomy of the wealthy is exercised through elective genetic screening while the basic survival of the marginalized remains a daily struggle. A truly ethical medical framework must transcend individual cases to address the systemic inequalities that dictate who is allowed to live a life of quality and who is relegated to the status of a biological statistic.",
    ),
    (
        "The Psychosomatic Bridge: Beyond Cartesian Dualism",
        "For centuries, Western medicine has operated under the shadow of Cartesian dualism, an ontological framework that separates the mind from the body as two distinct entities. However, modern neuroscience and psychoneuroimmunology are finally dismantling this divide, revealing a psychosomatic bridge where thoughts, emotions, and physical health are inextricably linked. The nuance of this integration is the realization that the placebo effect is not a nuisance to be eliminated in clinical trials, but a profound demonstration of the mind's innate capacity for healing. Consequently, treating a physical ailment without addressing the patient's psychological state is increasingly seen as a reductionist and incomplete approach. Embracing a holistic paradigm requires a shift in medical education, moving away from the body-as-a-machine metaphor toward a more sophisticated understanding of the human being as an integrated biological and emotional ecosystem.",
    ),
    (
        "The Socioeconomic Determinants of Health",
        "It is a common fallacy to believe that health is solely the result of individual choices and genetic luck. In reality, the most significant predictors of longevity and well-being are socioeconomic determinants-the conditions in which people are born, grow, live, and work. The nuance of this reality is the social gradient, where every step down the socioeconomic ladder is associated with a corresponding decrease in health outcomes. Factors such as food insecurity, unstable housing, and chronic exposure to environmental pollutants create a weathering effect on the body, leading to premature aging and chronic disease. Therefore, public health interventions that focus exclusively on lifestyle changes are often doomed to fail if they do not address the structural injustices that limit an individual's agency. True health equity requires a political commitment to redistributing resources and ensuring that the fundamental requirements for a healthy life are treated as universal rights rather than privileges of the affluent.",
    ),
    (
        "The Epistemological Crisis in Nutritional Science",
        "Nutritional science is currently embroiled in an epistemological crisis, characterized by a dizzying array of contradictory studies and shifting guidelines that have left the public in a state of profound confusion. One decade, fat is the primary villain of heart disease; the next, it is sugar that is blamed for the global obesity epidemic. The nuance of this instability lies in the inherent difficulty of conducting long-term, controlled dietary studies on humans, leading to a reliance on observational data that can easily be misinterpreted or influenced by industry funding. Furthermore, the reductionist approach of studying individual nutrients in isolation fails to account for the food matrix and the complex interactions between different ingredients. To navigate this uncertainty, we must move toward a more nuanced understanding of nutrition that prioritizes whole foods and cultural traditions over the latest superfood trends. Science is a process of refinement, but in the realm of nutrition, the influence of commercial interests often complicates the pursuit of objective truth.",
    ),
    (
        "The Paradox of the Healthy Obsession",
        "In our hyper-health-conscious society, the pursuit of wellness has, for some, morphed into a new form of pathology known as orthorexia nervosa-an obsession with eating pure and correct foods. This phenomenon highlights the paradox of modern well-being: the more we focus on optimizing our biology, the more we risk sacrificing our psychological and social health. The nuance of this obsession is the moralization of food, where dietary choices are used to signal one's virtue or superior self-control. This creates a culture of perpetual dissatisfaction, where the body is never quite efficient or clean enough. True health should incorporate a sense of spontaneity and pleasure, yet the current wellness industry often relies on fostering anxiety and insecurity to sell its products. We must learn to distinguish between the legitimate desire for health and the performative perfectionism that turns self-care into a source of chronic stress.",
    ),
    (
        "Neuroplasticity and the Architecture of the Mind",
        "The discovery of neuroplasticity-the brain's ability to reorganize itself by forming new neural connections throughout life-is one of the most revolutionary findings in modern science. It challenges the fatalistic view that the brain's architecture is fixed in early adulthood, offering profound hope for recovery from trauma and age-related decline. The nuance of this discovery, however, is that neuroplasticity is a double-edged sword; just as we can train our brains for resilience and focus, we can also inadvertently hardwire them for anxiety and distraction through chronic exposure to digital noise and stress. Consequently, the concept of mental hygiene takes on a new urgency. Our daily habits-what we read, who we talk to, and how we manage our attention-literally sculpt our neural pathways. Understanding this power places a tremendous responsibility on the individual to curate their mental environment with the same rigor that one might apply to their physical diet.",
    ),
    (
        "The Commercialization of Longevity",
        "The burgeoning longevity industry, valued at billions of dollars, promises to decode the secrets of aging through a combination of supplements, genetic editing, and high-tech interventions. While some of this research is grounded in legitimate science, much of it borders on a modern form of alchemy-the search for a digital fountain of youth. The nuance of this commercialization is the democratization of longevity, which is often marketed as a personal choice for those who are willing to pay for it. This narrative obscures the fact that the most effective interventions for a long life-rest, community, and fresh food-are not patentable and therefore receive far less investment. Furthermore, the fixation on extending lifespan often ignores the importance of healthspan-the period of life spent in good health. We must be cautious of a future where we spend our final decades in a state of technologically sustained frailty, having neglected the simple, non-commercial foundations of a life well-lived.",
    ),
    (
        "Collective Trauma and the Body Politic",
        "The field of somatics has long argued that trauma is not merely a psychological event but a physical one, stored in the tissues and the nervous system. When large groups of people experience systemic violence, displacement, or global crises, the result is a collective trauma that can affect the body politic for generations. The nuance of this phenomenon is its intergenerational transmission; epigenetics suggests that the biological markers of stress can be passed down from parents to children, even in the absence of the original threat. Consequently, addressing a society's health issues requires more than individual therapy; it necessitates a process of collective healing and truth-telling. Acknowledging the physical reality of historical and systemic trauma is a prerequisite for creating a healthier future. If the body politic is to heal, we must create social structures that provide the safety and belonging necessary for the nervous system to move out of a permanent state of high alert.",
    ),
    (
        "The Philosophy of Pain: Beyond Sensation",
        "Pain is one of the most universal yet intensely private human experiences, existing at the intersection of physiology, psychology, and culture. While traditional medicine often treats pain as a straightforward signal of tissue damage, the reality is far more nuanced. Chronic pain, in particular, can become a centralized condition where the nervous system remains in a state of hypersensitivity long after the physical injury has healed. Furthermore, the experience of pain is heavily modulated by the sufferer's emotional state, cultural background, and expectations. This complexity makes the current opioid-centric approach to pain management dangerously reductionist, as it treats a multidimensional problem with a unidimensional tool. A more sophisticated philosophy of pain would acknowledge the meaning of the sensation to the patient and integrate physical therapies with psychological support. By moving beyond the view of pain as a purely mechanical failure, we can develop more compassionate and effective ways to support those living in its shadow.",
    ),
]


HEALTH_TEXTS["c2"] = [
    (
        "The Ontological Paradox of Longevity: Seeking the Indefinite",
        "The contemporary obsession with life extension, often framed within the seductive rhetoric of biological optimization, reveals a profound ontological paradox. As we deploy sophisticated biotechnological interventions to postpone the inevitability of senescence, we inadvertently transform the nature of the human experience itself. The pursuit of an indefinite lifespan assumes that the self is a static entity that can be preserved through the mere maintenance of cellular integrity. However, a C2-level critique must interrogate whether the meaning of life is inextricably linked to its finitude. If death is removed from the horizon of human expectation, does the temporal structure of our ambitions, relationships, and creative impulses collapse? The nuance of this pursuit lies in the danger of achieving a quantitative victory over time at the expense of qualitative depth. To exist in a state of technologically sustained stasis is not necessarily to live; it is, perhaps, merely to persist in a curated biological vacuum where the existential urgency of the now is dissipated by the promise of an infinite tomorrow.",
    ),
    (
        "The Epistemology of Wellness: Science vs. Subjective Vitality",
        "The burgeoning wellness industry operates at a complex epistemological intersection where rigorous clinical data meets the nebulous realms of ancient wisdom and subjective feeling. We are increasingly encouraged to quantify the self through biomarkers, sleep scores, and genetic predispositions, treating the body as a decipherable data set. Yet, the nuance of true well-being-vitality-remains stubbornly resistant to total quantification. There is a profound discrepancy between the medical absence of disease and the subjective presence of health. To rely solely on the metric is to risk an estrangement from the lived body, where we trust the algorithm over our own internal proprioception. A sophisticated understanding of health requires the synthesis of these disparate epistemologies; it acknowledges the objective reality of biology while honoring the subjective, irreducible experience of being alive. True wellness is not the sum of one's data points, but the harmonious resonance between the physical organism and the conscious mind.",
    ),
    (
        "The Ethics of Neuro-Enhancement and the Post-Human Frontier",
        "The advent of pharmacological and technological neuro-enhancement-from sophisticated nootropics to potential brain-computer interfaces-promises to augment the cognitive architecture of the human mind. While the potential to ameliorate neurodegenerative decline is a clear moral imperative, the use of these tools for enhancement in healthy individuals presents a labyrinth of bioethical dilemmas. The nuance of this shift involves the potential erosion of the authentic self. If our creativity, focus, and emotional resilience become the products of chemical or digital modulation, to whom do our achievements truly belong? Furthermore, in a hyper-competitive society, the choice to enhance one's cognition may quickly become a de facto requirement for survival, creating a stratified cognitive hierarchy based on socioeconomic access. We must confront the possibility that in our quest for a more efficient mind, we are inadvertently engineering the obsolescence of the very human qualities-struggle, error, and organic growth-that define our species.",
    ),
    (
        "The Somatic Echo of Historical Trauma: An Epigenetic Meditation",
        "Emerging research in epigenetics suggests that the biological impact of profound trauma is not confined to the individual lifespan but can leave a somatic echo in the genetic expression of subsequent generations. This realization challenges our Western, individualistic conception of health, suggesting that our current physiological state is, in part, a historical document. The nuance of intergenerational trauma is that the body politic and the biological body are one and the same. To address the chronic health crises of marginalized populations without acknowledging the intergenerational stress of systemic displacement or violence is to treat a symptom while ignoring the source. A C2-level approach to public health must integrate this deep time of biology, recognizing that healing the individual requires a process of collective, historical reckoning. We are not merely isolated organisms; we are the biological culmination of our ancestors' resilience and their suffering.",
    ),
    (
        "The Commodification of Mindfulness: From Liberation to Productivity",
        "Originally conceived as a path to spiritual liberation and the dismantling of the ego, mindfulness has been systematically commodified by the neoliberal wellness industry and repurposed as a tool for corporate productivity. The nuance of this transformation is the privatization of stress. By framing mindfulness as a personal responsibility for mental maintenance, the systemic causes of anxiety-precarious labor, social isolation, and environmental decay-are conveniently obscured. We are encouraged to breathe through the dysfunctions of a broken system rather than seeking to change the system itself. This McMindfulness offers a sanitized, apolitical version of a radical practice, serving to pacify the individual rather than empower them. To reclaim the true power of mindfulness, we must move beyond the commodified stress-reduction model and return to a practice that fosters a critical awareness of our interconnectedness and our social obligations.",
    ),
    (
        "The Architecture of the Modern Malaise: Urbanism and Biology",
        "The modern urban environment is frequently at odds with our evolutionary biology, creating a mismatch that manifests as chronic systemic inflammation and psychological distress. The nuance of this malaise lies in the subtle ways our sensory environment dictates our hormonal state. The absence of natural light rhythms, the constant auditory assault of the city, and the nature-deficit of high-density living keep the human nervous system in a state of low-level, perpetual vigilance. We treat these symptoms with pharmaceuticals, yet the cause is architectural and structural. A sophisticated view of health recognizes that the city is a biological actor. Healthy urbanism is not just about the presence of clinics, but about the integration of fractals, green spaces, and social nodes that align with our innate biological needs for belonging and biophilia. We cannot be truly healthy in an environment that treats us as mechanical units of production rather than biological organisms.",
    ),
    (
        "The Philosophy of the Placebo: The Mind as a Biological Agent",
        "The placebo effect is often dismissed in clinical trials as a nuisance variable to be controlled for, yet it represents one of the most profound mysteries of medicine: the mind's capacity to initiate biological healing through the mediation of belief and expectation. The nuance of the placebo is that it is not nothing acting on the body; it is the body's own internal pharmacy being activated by a symbolic gesture. This suggests that the meaning of a treatment is a biological variable in its own right. A C2-level analysis of healing must move beyond the purely biochemical model to acknowledge this meaning-response. If the ritual of care, the empathy of the clinician, and the patient's own narrative of recovery are essential to the biological outcome, then the current trend toward cold, algorithmic medicine is a significant scientific error. Healing is as much a semiotic process as it is a chemical one.",
    ),
    (
        "The Biopolitics of the Normal Body",
        "The concept of normal health is an ideological construct that has been used historically to marginalize and discipline bodies that deviate from a specific, idealized standard. Whether through the lens of the Body Mass Index, BMI, or neuro-typicality, the medical gaze often pathologizes diversity in favor of a sanitized, productive norm. The nuance of this biopolitics is that the healthy body is frequently equated with the compliant and efficient body. We must interrogate who defines the parameters of health and to what end. A truly inclusive philosophy of well-being would celebrate neuro-diversity and body-neutrality, recognizing that health is a subjective spectrum rather than a rigid binary. To reclaim sovereignty over our own bodies, we must deconstruct the internalized norm and honor the unique, often non-linear ways in which different organisms find their own state of balance.",
    ),
    (
        "The Pathological Pursuit of Purity: Orthorexia and Modern Anxiety",
        "In an era characterized by a lack of traditional moral anchors, the pursuit of pure nutrition has become a secular religion for many, leading to the emergence of orthorexia nervosa. This obsession with dietary purity is less about biological health and more about a desperate attempt to gain control over an increasingly unpredictable and toxic world. The nuance of this disorder is that it is often socially rewarded as extreme discipline or health consciousness. However, when the fear of contamination leads to social isolation and psychological rigidity, the pursuit of health becomes a source of profound illness. We must recognize that a healthy organism is characterized by resilience and flexibility, not by a fragile adherence to a restrictive protocol. True vitality requires the ability to tolerate the imperfect and the uncontrolled, acknowledging that a life lived in fear of a chemical or a calorie is a life lived in a psychological prison.",
    ),
    (
        "The Metaphysics of the Immune System: Self vs. Other",
        "The immune system is fundamentally a biological mechanism of recognition-a way for the organism to distinguish between the self and the other. However, in cases of autoimmune disease, this fundamental distinction collapses, and the body begins a tragic process of self-immolation. The nuance of this biological failure mirrors our current social and philosophical crises of identity. If we perceive everything outside of ourselves as a threat, we end up destroying our own foundations. A C2-level meditation on immunity suggests that health is not the absolute exclusion of the other, but the capacity for tolerogenic interaction. We thrive through symbiosis and the integration of foreign elements, as evidenced by our microbiome. Health, therefore, is not a fortress but an open, discerning system. The goal of a sophisticated medicine should be to foster this capacity for discernment, allowing the organism to engage with the world without losing its own essential integrity.",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, estruturas de repeticao e vocabulario concreto",
    "a1": "rotinas de saude, conectores simples e vocabulario de alimentos e corpo",
    "a2": "passado simples, comparativos e adjetivos descritivos",
    "b1": "opinioes, causa e consequencia, conectores variados",
    "b2": "argumentacao, tendencias, ciencia e vocabulario tecnico-medico",
    "c1": "nuance, estilo, discussoes bioeticas e inferencia profunda",
    "c2": "registro erudito, inferencia, ambiguidade e densidade filosofica",
}


class Command(BaseCommand):
    help = "Replace the Saude e bem-estar catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="saude-e-bem-estar")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = HEALTH_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-saude-e-bem-estar-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Saude e bem-estar texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre saude e bem-estar: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D cartoon style, clean lines, high quality, "
            f"educational health and wellness scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
