import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


TECH_TEXTS = {
    "iniciante": [
        (
            "The Robot and the Tablet",
            "Roo is a small, happy robot. It has two big eyes. Roo lives in a cozy tech lab. A student, Maria, has a new tablet. Roo looks at the tablet. Roo is curious. Maria shows Roo a friendly app. Roo smiles. Technology is fun for Roo. Maria smiles, too.",
        ),
        (
            "The Smart Watch",
            "Sam has a new smart watch. The watch is round and black. It sits on Sam's wrist. The watch shows the time. It counts Sam's steps, too. Sam walks in the park. The watch beeps. Sam looks at the screen. The watch is a helpful tool. Sam is happy with the tech.",
        ),
        (
            "The Blue Camera",
            "Lina has a blue digital camera. The camera is very small. Lina goes to the garden. She sees a beautiful flower. Lina clicks a button. The camera saves the photo. The photo is clear and bright. Lina looks at the screen. She likes her new camera. Photography is a great hobby.",
        ),
        (
            "The Solar Panel",
            "The house has a big solar panel. The panel is on the roof. The sun is very hot today. The sun hits the solar panel. The panel makes clean energy. Now, the lights are on. The TV is on, too. The family is happy. The sun helps the house. Technology is good for nature.",
        ),
        (
            "The New Headphones",
            "Tom has large grey headphones. The headphones are soft. Tom puts the headphones on. He connects them to his phone. Tom listens to a podcast. The sound is very quiet and clear. Tom sits on the sofa. He learns new things. The headphones help Tom study. He is very calm today.",
        ),
        (
            "The Computer Mouse",
            "A computer mouse is on the desk. It is a wireless mouse. The mouse is ergonomic and fast. Julia moves the mouse. The cursor moves on the screen. Julia clicks on a file. The file opens quickly. The mouse is a simple tool. It helps Julia with her work. Julia likes her office.",
        ),
        (
            "The Smart Light",
            "The bedroom has a smart light. The light is white. Leo has an app on his phone. Leo touches the screen. The light turns blue. Leo touches the screen again. The light turns yellow. The smart light is very cool. Leo is in bed. He is ready to sleep. Goodnight, technology.",
        ),
        (
            "The Gaming Console",
            "The gaming console is under the TV. It is a black box. Pedro has a controller in his hands. He plays a racing game. The car is fast and red. Pedro wins the race. The graphics are beautiful. Pedro plays with his friends online. Gaming is a fun activity. Pedro smiles and laughs.",
        ),
        (
            "The WiFi Router",
            "A small box is on the shelf. It is a WiFi router. The router has three green lights. The lights blink fast. The internet is strong in the house. Sarah uses her laptop. She watches a video. The video does not stop. The router works well. Sarah finishes her homework. Technology is fast.",
        ),
        (
            "The Electric Scooter",
            "The scooter is silver and orange. It is an electric scooter. Marco stands on the scooter. He goes to the university. The scooter is fast and quiet. It does not use gas. Marco is happy. He saves time every day. The battery is full. Marco arrives at the class. Electric travel is easy.",
        ),
    ],
    "a1": [
        (
            "My Daily Laptop Routine",
            "Every morning, I open my laptop on the desk. First, I check my emails for school. My laptop is fast and very light. Then, I use a website to practice English. I like to use headphones because the sound is very clear. In the afternoon, I watch videos about new gadgets. My brother also uses the computer to play games. We always charge the battery at night. Using technology is part of my daily routine. It helps me study and talk to my friends easily.",
        ),
        (
            "The Smart Kitchen",
            "My aunt has a very modern kitchen with new technology. She has a smart refrigerator with a big screen. The refrigerator tells her when the milk is finished. She also has a digital oven. It connects to her smartphone, so she can start cooking from the living room. In the morning, a smart coffee machine makes coffee automatically. My aunt loves these gadgets because they save a lot of time. She says that technology makes cooking simple and fun for everyone in the family.",
        ),
        (
            "Learning with a Tablet",
            "In my classroom, every student has a tablet for lessons. We use the tablets to read digital books and watch educational videos. My teacher sends the homework to our tablets every Friday. I like the tablet because it is easier to carry than heavy books. Sometimes, we play learning games in groups. It is very exciting when my team wins. However, we must be careful with the screen. We only use the tablets for one hour because our eyes need a rest. Technology is a great friend in my school.",
        ),
        (
            "The New Virtual Reality Headset",
            "Last week, my cousin bought a virtual reality headset. It looks like big goggles. When you put them on, you see a completely different world. I tried it and I was in a forest with dinosaurs. It felt very real because I could look in all directions. My cousin likes to play sports games with the headset. He moves his arms and jumps in the living room. It is a very active way to play video games. We think this technology is the future of entertainment and education.",
        ),
        (
            "A Visit to the Tech Store",
            "Today, I am at a large tech store with my father. There are many new smartphones and smartwatches on the shelves. I am looking at a new drone with a 4K camera. The drone is small, but it can fly very high. My father wants to buy a new television for the house. He likes the screens with vivid colors. We talk to a friendly assistant about the prices and the battery life of the gadgets. The store is very crowded because there is a big sale today.",
        ),
        (
            "The GPS Adventure",
            "My family is on a road trip to a small village. We do not have a paper map, so we use the GPS on the car's dashboard. A calm voice tells my father when to turn left or right. The GPS is very helpful because it shows the traffic and the fastest way. Sometimes, the signal is weak in the mountains, but it quickly returns. My mother uses her phone to find a good restaurant nearby. Thanks to technology, we never get lost and we find beautiful places easily.",
        ),
        (
            "Printing a 3D Toy",
            "My older brother has a 3D printer in his bedroom. It is a fascinating machine that creates real objects from plastic. Yesterday, he printed a small blue robot for me. First, he designed the robot on his computer. Then, the printer started to work slowly. It took three hours to finish the toy. The 3D printer uses heat to melt the plastic and build the layers. I think it is amazing that we can make our own toys at home now with this technology.",
        ),
        (
            "Security at Home",
            "My house has a smart security system. There is a small camera near the front door. When someone rings the bell, my mother sees their face on her smartphone. She can talk to the person even when she is at work. We also have smart locks that open with a code or a fingerprint. This technology makes my family feel very safe. At night, the system turns on the outdoor lights automatically. It is a very clever way to protect our home using the internet and sensors.",
        ),
        (
            "The Digital Library",
            "I do not go to the physical library very often now. I have a digital library app on my e-reader. I can download hundreds of books in a few seconds. The e-reader is great because the battery lasts for many weeks. I like to read at night before I go to sleep. The screen is special and it does not hurt my eyes. My favorite category is Science Fiction. My friends and I share our favorite books using a QR code. Digital reading is cheap and very convenient for students.",
        ),
        (
            "My First Robot Vacuum",
            "We have a new robot vacuum cleaner in our apartment. It is a small, round machine that moves on the floor. It has sensors, so it does not hit the furniture or the walls. Every day at 10 AM, the robot starts cleaning the carpets. My dog is very curious and follows the robot around the kitchen. When the battery is low, the robot goes back to its station to charge. It is a very useful gadget because my parents are always busy. Our floor is always clean now!",
        ),
    ],
    "a2": [
        (
            "The First Smartphone Memory",
            "Ten years ago, my father bought his first smartphone. It was much smaller than the phones we use today, and the screen was not very bright. He used it primarily to take photos and send simple messages. I remember that the battery lasted for a long time compared to my current device. Last weekend, we found it in a drawer and compared his old phone with my new one. My phone is significantly faster and has a much better camera. However, he said the old phone was simpler and less distracting. We laughed at the old ringtones and the slow internet. This comparison showed me how fast technology changes every year. Now, smartphones are like powerful small computers in our pockets, but sometimes I miss the simplicity of the past.",
        ),
        (
            "A Lesson in Coding",
            "Last semester, Noah started a basic coding class at school. At first, he thought that programming was only for geniuses, but his teacher explained that it is just like learning a new language. In the first week, they used a simple program to move a digital character across the screen. Noah practiced every day on his laptop. He learned how to create a loop and how to fix small errors in his code. By the end of the month, he designed a simple game where a cat catches a ball. He felt very proud because his friends played the game and liked it. Coding taught Noah that discipline and patience are very important. Now, he wants to study software engineering in the future because he loves creating new tools.",
        ),
        (
            "The Evolution of Music Players",
            "My grandfather told me stories about how people listened to music when he was young. In the past, they used large vinyl records and later, small plastic cassette tapes. He said that you couldn't skip songs easily like we do now. In the 1990s, portable CD players became popular, but they were bulky and sometimes stopped playing if you walked too fast. Today, we have streaming services on our phones that hold millions of songs. Music is much more accessible now than it was fifty years ago. I can listen to any artist from any country in seconds. My grandfather thinks the sound of the old records is warmer, but he agrees that digital music is more convenient for traveling. It is amazing to see how technology changed our relationship with art.",
        ),
        (
            "The Smart Classroom Experiment",
            "Our school recently transformed my classroom into a Smart Room. They installed an interactive whiteboard and gave every student a digital stylus. Last Tuesday, we had a geography lesson about volcanoes. Instead of just looking at pictures in a book, we used virtual reality glasses to stand near a digital volcano. The experience was much more exciting than a traditional lesson. We could see the lava moving and hear the sound of the explosion. The teacher explained that technology helps students visualize difficult concepts. However, we still use paper and pens for some activities because writing by hand helps our memory. The smart classroom is a great balance between modern innovation and classic study methods. I feel more motivated to go to school every morning now.",
        ),
        (
            "How I Fixed My Tablet",
            "Two days ago, my tablet stopped working. The screen stayed black and it didn't charge. I was worried because all my school projects were saved on it. Instead of going to a repair shop immediately, I decided to look for a solution online. I found a video tutorial that explained how to perform a hard reset. I followed the instructions carefully: I pressed the power button and the volume button at the same time for ten seconds. Suddenly, the silver logo appeared and the tablet turned on again! It was a simple software problem, not a broken screen. I felt like a real technician. This experience taught me that we can use the internet to learn how to solve practical problems and save money.",
        ),
        (
            "The Drones of the Future",
            "Last summer, I visited a technology fair in Brasilia with my classmates. The most popular attraction was the drone racing competition. Drones are small flying machines controlled by a remote or a smartphone. In the past, only the military used them, but now they are used for photography, delivery, and even agriculture. At the fair, a scientist showed us a drone that delivers medicine to remote villages. It was faster and cheaper than using a truck. We also saw tiny drones that can check the health of plants on a farm. My friend Lucas bought a small drone to take aerial photos of his house. I think that in a few years, the sky will be full of these helpful machines.",
        ),
        (
            "My Digital Detox Weekend",
            "Last month, I decided to try a digital detox for forty-eight hours. This means I didn't use my phone, my laptop, or my gaming console for the entire weekend. On Saturday morning, I felt a bit anxious because I wanted to check my messages. However, I decided to go for a walk in the park instead. I noticed the green trees and the sound of the birds more than usual. I also read a physical book and played a board game with my family. By Sunday evening, I felt very calm and my eyes were not tired. Although I love technology and use it for my software engineering studies, this experiment showed me that offline time is essential for health.",
        ),
        (
            "The History of the Internet",
            "Did you know that the internet was very different thirty years ago? My teacher told us that in the beginning, websites only had text and no images. The connection was very slow and it made a strange noise when you connected the phone line. You couldn't use the telephone and the internet at the same time! People used the internet mostly for emails and basic research. Today, the internet is everywhere-in our watches, cars, and even refrigerators. We use it for video calls, streaming movies, and working from home. It is the most important invention of the last century because it connected the whole world. I cannot imagine my life as a student without the help of a fast connection.",
        ),
        (
            "The Robot in the Hospital",
            "Last week, I read an interesting article about a robot named Moxi that works in a big hospital. Moxi is not a doctor, but it helps the nurses with heavy work. It can carry medicine, water, and clean blankets to different rooms. The robot has a long arm and a friendly digital face. The nurses like Moxi because they have more time to talk to the patients and help them with their pain. The robot uses sensors to move around people and equipment without hitting anything. Technology like this is very useful because it makes the hospital more efficient. My mother is a nurse and she thinks a robot helper would be a great idea for her department too.",
        ),
        (
            "Artificial Intelligence in Art",
            "I recently discovered an app that uses Artificial Intelligence to create paintings. I typed a futuristic city with blue lights into the search bar, and the AI generated a beautiful image in less than one minute. It looked like a professional artist painted it! I showed the picture to my friend Geovanna, and we discussed if this is real art. Some people think that AI is a threat to human artists, but others believe it is just a new tool, like a digital brush. I used the AI to create a cover for my school report. It was very helpful and saved me a lot of time. Technology and creativity are working together more and more every day.",
        ),
    ],
    "b1": [
        (
            "The Impact of Social Media on Communication",
            "Social media has fundamentally changed how we communicate with each other in the modern world. Today, most people use platforms like Instagram, TikTok, or WhatsApp to share moments of their lives and stay connected with family. One major consequence of this digital shift is that news travels almost instantly across the globe. For instance, if a significant event occurs in Tokyo, people in Brasilia will know about it within seconds. However, there are also negative aspects to consider regarding our mental health. Some experts believe that many individuals spend too much time staring at screens instead of engaging in face-to-face conversations. Consequently, many teenagers may feel lonely even when they have thousands of virtual followers. In my opinion, technology is a fantastic tool for connectivity, but we must use it with balance. If we learn to control our screen time and prioritize real-world interactions, we can enjoy the benefits of social media without the stress of constant notifications. Therefore, finding a middle ground between the digital environment and real life is essential for a healthy lifestyle.",
        ),
        (
            "The Future of Remote Work",
            "The concept of the traditional office is changing rapidly due to advancements in communication technology. A few years ago, working from home was a rare luxury, but today it has become a standard practice for many companies in the software engineering sector. This shift happened because high-speed internet and video conferencing tools, such as Zoom and Teams, allow employees to collaborate effectively from anywhere. One benefit of remote work is the flexibility it offers; employees can save hours every day because they do not have to travel through heavy traffic. On the other hand, some people argue that working from home can be isolating. Without the physical presence of colleagues, it is sometimes difficult to maintain a strong team spirit. Furthermore, the line between professional and personal life often becomes blurred. To be successful in this new environment, discipline is required to set a clear schedule. In conclusion, while remote work offers great freedom, it also demands better self-management and a dedicated workspace to ensure productivity remains high.",
        ),
        (
            "Cybersecurity: Protecting Your Digital Identity",
            "As we move more of our lives online, cybersecurity has become one of the most critical issues of our time. Every time we shop online or use social media, we share personal data that could be targeted by hackers. The main cause of digital fraud is often the use of weak passwords or clicking on suspicious links in emails. Consequently, many people lose access to their accounts or even have their financial information stolen. To prevent this, it is highly recommended to use two-factor authentication on all important accounts. This simple step adds an extra layer of security that makes it much harder for unauthorized users to gain access. Moreover, software engineering students are now developing advanced middleware to detect fraud before it happens. In my view, being proactive about digital safety is not just a choice; it is a necessity. By educating ourselves about common threats and keeping our software updated, we can significantly reduce the risks associated with the digital world.",
        ),
        (
            "The Rise of E-learning and Digital Education",
            "Education has been completely transformed by digital platforms and the internet. E-learning allows students from all over the world to access high-quality courses from prestigious universities without leaving their homes. This is particularly useful for autodidacts who want to learn specific skills, such as a new programming language or a foreign language. The primary advantage is that students can learn at their own pace, which is much more efficient than a rigid traditional classroom schedule. However, digital education also presents challenges, such as the need for a stable internet connection and high levels of self-motivation. Without a teacher physically present to encourage them, some students may struggle to finish their courses. In addition, the lack of social interaction with peers can make the learning process feel less engaging. Despite these drawbacks, the accessibility of online resources is an incredible achievement. As technology continues to evolve, e-learning will likely become the primary method for professional development in the future.",
        ),
        (
            "Smart Cities: Technology for Urban Life",
            "The idea of a Smart City involves using technology and data to improve the quality of life for citizens. By installing sensors and using Artificial Intelligence, cities can manage traffic, energy use, and waste collection more efficiently. For example, smart traffic lights can change their timing based on real-time traffic flow, which reduces congestion and pollution. Consequently, people spend less time in their cars and the air quality in the city improves. Furthermore, smart lighting systems can dim the streetlights when no one is around, saving a significant amount of electricity. While these innovations are exciting, they also raise concerns about privacy and the massive cost of infrastructure. If a city is constantly monitoring its citizens to gather data, where do we draw the line? In my opinion, the transition to smart cities is inevitable and beneficial, provided that the data collected is handled ethically and transparently to protect the rights of the residents.",
        ),
        (
            "Renewable Energy and Green Tech",
            "In the fight against climate change, technology is our most powerful ally. Green Tech refers to innovations that help protect the environment by reducing carbon emissions and promoting sustainability. The most common examples are solar panels and wind turbines, which provide clean energy without burning fossil fuels. Because the cost of these technologies has decreased significantly over the last decade, many families and businesses are now installing their own energy systems. This shift is vital because it reduces our dependence on coal and oil, which are the main causes of global warming. In addition to energy production, new technologies are improving recycling processes and water management. For instance, smart sensors can detect leaks in city pipes, preventing the waste of thousands of liters of water. Although the transition to a green economy is expensive, the long-term consequences of doing nothing would be far more costly. Technology gives us the tools to build a sustainable future if we have the political will to implement it.",
        ),
        (
            "The Ethical Dilemma of Facial Recognition",
            "Facial recognition technology is becoming increasingly common in airports, smartphones, and even public streets. While it offers great convenience, such as unlocking your phone instantly or speeding up security checks, it also sparks intense ethical debates. The primary benefit is security; police can use the technology to find missing persons or identify criminals in a crowd. However, many people argue that constant surveillance is a violation of basic human rights and privacy. If governments use this technology without strict regulations, it could lead to a society where everyone is tracked at all times. Furthermore, studies have shown that facial recognition algorithms are not always accurate and can have biases against certain groups of people. Consequently, several cities have already banned the use of this technology by the police. In my view, we need a global conversation about how to balance public safety with individual freedom as this technology becomes even more sophisticated.",
        ),
        (
            "How Smartphones Changed Our Brains",
            "It is hard to remember a time when we didn't have all the information in the world in our pockets. Smartphones have changed not only how we live but also how our brains function. Because we can find any fact on Google in seconds, we are becoming less reliant on our long-term memory. Some scientists call this the Google Effect, where we forget information because we know we can find it again online. On the positive side, our ability to multitask and process visual information quickly has improved. We are becoming experts at filtering through vast amounts of data to find what is relevant. However, the constant stream of notifications can reduce our attention span and make it difficult to focus on deep, complex tasks. To mitigate these effects, many people are now practicing mindful tech use, which involves setting specific times to be offline. Understanding how technology affects our psychology is the first step toward maintaining a healthy relationship with our devices.",
        ),
        (
            "The Internet of Things in Our Homes",
            "The Internet of Things, or IoT, refers to the network of physical objects-like fridges, thermostats, and lights-that are connected to the internet. In a smart home, these devices communicate with each other to make life more comfortable and efficient. For example, your thermostat can learn your schedule and lower the temperature when you are at work, which saves energy and reduces your monthly bills. You can also control your home's security cameras and locks from your smartphone while you are on vacation. While this connectivity is very convenient, it also creates new security risks. If a device is connected to the internet, it can potentially be hacked. Therefore, it is crucial to keep the software on all smart devices updated and use secure networks. Despite the risks, the IoT market is growing rapidly because the benefits of automation and energy efficiency are very attractive to modern homeowners.",
        ),
        (
            "Wearable Tech: Beyond the Smartwatch",
            "When we think of wearable technology, the first thing that comes to mind is usually a smartwatch that tracks our steps and heart rate. However, the field is expanding into much more advanced areas, such as smart clothing and medical devices. For instance, there are now smart socks for runners that analyze their technique to prevent injuries. In the medical field, wearable sensors can monitor glucose levels in diabetic patients and send the data directly to their doctors in real-time. This is a huge advancement because it allows for continuous monitoring without the need for frequent hospital visits. Furthermore, researchers are developing smart glasses that can provide augmented reality information directly to the user's eyes. As these devices become smaller and more stylish, they will likely become as common as smartphones. The integration of technology into our clothing and bodies represents the next frontier of the digital revolution, making our lives more data-driven than ever before.",
        ),
    ],
}


TECH_TEXTS["b2"] = [
    (
        "The Rise of Artificial Intelligence: A New Frontier",
        "Artificial Intelligence is no longer a concept confined to the realms of science fiction; it is a transformative reality that permeates our daily lives. From virtual assistants that recognize our nuances to algorithms that predict our consumer behavior, AI is ubiquitous. While many herald this as a massive leap forward for productivity, others express profound concerns regarding job displacement and data privacy. The primary argument for AI focuses on unparalleled efficiency. In healthcare, for instance, AI can analyze thousands of medical records in minutes, aiding doctors in identifying diseases with pinpoint precision. On the flip side, the automation of cognitive tasks could lead to the disappearance of traditional roles across various sectors. It is, undeniably, a double-edged sword that necessitates rigorous ethical regulation. We must ensure that these abstract algorithms do not inadvertently reinforce societal biases or infringe upon personal freedoms. To truly wrap your head around the scale of this change, one must view AI not as a replacement for human intelligence, but as a powerful engine that requires a responsible driver at the wheel.",
    ),
    (
        "Blockchain Beyond Cryptocurrency",
        "When people hear the word blockchain, they almost instinctively think of Bitcoin or digital currencies. However, the underlying technology-a decentralized, immutable ledger-has applications that extend far beyond financial transactions. In its simplest form, blockchain allows information to be stored across a network of computers, making it nearly impossible to hack or alter without detection. This transparency is a game-changer for supply chain management. For example, a consumer could scan a QR code on a carton of milk and see the entire journey from the farm to the supermarket shelf. Furthermore, smart contracts can automate legal agreements without the need for intermediaries, potentially saving billions in administrative costs. Despite its potential, blockchain faces significant hurdles, including high energy consumption and a lack of clear international legislation. As we move forward, the challenge will be to balance the decentralized nature of the technology with the need for security and sustainability. It remains to be seen whether blockchain will fulfill its promise of a more transparent world.",
    ),
    (
        "The Psychological Cost of Constant Connectivity",
        "In the digital age, being offline has become a rare state of being. While constant connectivity allows us to access information and maintain relationships with ease, it also exacts a psychological toll that we are only beginning to understand. The phenomenon of Fear of Missing Out is a prime example of how social media can induce anxiety and a sense of inadequacy. When we are constantly bombarded with the highlights of other people's lives, it is easy to lose sight of our own reality. Moreover, the attention economy is designed to keep us scrolling, often at the expense of our sleep and mental clarity. Research suggests that the constant stream of notifications fragments our focus, making it increasingly difficult to engage in deep work or meaningful reflection. To combat this, many are turning to digital minimalism-a philosophy that encourages intentional use of technology. By setting strict boundaries and reclaiming our offline time, we can mitigate the negative effects of the digital world. Ultimately, technology should serve our well-being, not diminish our quality of life.",
    ),
    (
        "The Future of Transportation: Autonomous Vehicles",
        "The prospect of self-driving cars roaming our city streets is moving closer to reality every day. Proponents of autonomous vehicles argue that they will drastically reduce traffic accidents, most of which are caused by human error, such as distraction or fatigue. Imagine a world where elderly or disabled individuals have newfound independence, and traffic congestion is a thing of the past because cars can communicate with each other to optimize flow. However, the transition to fully autonomous transport is fraught with ethical and technical dilemmas. One of the most discussed issues is the trolley problem-how should a car be programmed to react in an unavoidable accident? Should it prioritize the safety of its passengers or the pedestrians outside? Furthermore, the potential loss of millions of driving jobs could have severe economic consequences. While the technology is impressive, society must grapple with these abstract moral questions before autonomous cars become a ubiquitous part of our infrastructure. The road to a driverless future is paved with both innovation and uncertainty.",
    ),
    (
        "Cybersecurity in the Era of Quantum Computing",
        "As we develop more powerful computers, the methods we use to protect our data must also evolve. Current encryption standards, which safeguard everything from bank accounts to state secrets, rely on mathematical problems that are too complex for traditional computers to solve. However, the advent of quantum computing threatens to render these safeguards obsolete. A quantum computer operates using qubits, allowing it to perform calculations at speeds that were previously unimaginable. This means that a process that would take a modern supercomputer thousands of years could be completed by a quantum machine in seconds. Consequently, the cybersecurity industry is in a race to develop quantum-resistant encryption. This is an abstract but critical battle; if our security measures fail to keep pace, the integrity of the entire global digital infrastructure could be compromised. Engineers must think several steps ahead to ensure that the privacy we take for granted today survives the quantum revolution of tomorrow.",
    ),
    (
        "The Impact of 5G on the Internet of Things",
        "The rollout of 5G technology is often marketed as just a way to download movies faster, but its true significance lies in its capacity to power the Internet of Things. 5G offers ultra-low latency and the ability to connect a massive number of devices simultaneously. This is the nervous system that will enable smart cities to function in real-time. From streetlights that adjust based on foot traffic to trash cans that signal when they are full, the efficiency gains are staggering. In the industrial sector, 5G allows for the remote operation of heavy machinery with incredible precision, reducing risks for workers. Nevertheless, the rapid expansion of 5G also raises valid concerns regarding infrastructure costs and the security of a world where everything is interconnected. The more devices we connect, the more entry points we create for potential cyberattacks. As we embrace the 5G era, the focus must shift from mere speed to the resilience and security of our interconnected systems.",
    ),
    (
        "Digital Literacy: The Most Important Skill of the 21st Century",
        "In a world saturated with information, being able to read and write is no longer enough; we must also be digitally literate. Digital literacy involves more than just knowing how to use a computer; it is the ability to critically evaluate information, understand privacy settings, and navigate the ethical complexities of the internet. One of the most pressing challenges today is the spread of fake news and deepfakes, which can manipulate public opinion with alarming ease. Without the skills to distinguish between credible sources and misinformation, individuals are vulnerable to manipulation. Furthermore, as automation reshapes the job market, digital literacy is becoming a prerequisite for employment in almost every sector. Schools and universities must adapt their curricula to ensure that students are not just consumers of technology, but informed and responsible digital citizens. The digital divide is no longer just about who has access to the internet, but who has the skills to use it effectively.",
    ),
    (
        "The Evolution of E-commerce and Consumer Habits",
        "The way we shop has undergone a radical transformation over the last two decades. E-commerce has evolved from a niche convenience into a global behemoth that dictates the survival of traditional retail. The convenience of one-click shopping and doorstep delivery has irrevocably changed consumer expectations. We now expect instant gratification and a personalized shopping experience, driven by AI algorithms that know our preferences better than we do. However, this shift has significant environmental and social implications. The sheer volume of packaging waste and the carbon footprint of global shipping are major concerns for sustainability. Additionally, the dominance of a few tech giants has put immense pressure on small businesses that struggle to compete on price and logistics. As consumers, we have the power to influence this trend by choosing to support local businesses and demanding more sustainable practices from major retailers. The future of commerce is digital, but it must also be ethical and sustainable.",
    ),
    (
        "Augmented Reality: Blurring the Lines of Reality",
        "While Virtual Reality immerses you in a completely different world, Augmented Reality overlays digital information onto the real world. You might have seen this in mobile games or apps that let you place furniture in your room before you buy it. The potential for AR in professional training and education is immense. Surgeons can use AR to see a 3D overlay of a patient's internal organs during surgery, and mechanics can follow digital instructions projected onto the engine they are repairing. This technology enhances our perception of reality without disconnecting us from it. However, the widespread use of AR glasses also raises privacy concerns. If people are constantly wearing devices that can record everything they see, the concept of a private space might vanish. Moreover, the constant overlay of digital data could lead to information overload, making it difficult to appreciate the world as it is. AR is a powerful tool for productivity, but we must be careful not to lose our sense of presence in the physical world.",
    ),
    (
        "The Ethics of Gene Editing and Biotechnology",
        "Advancements in biotechnology, specifically CRISPR technology, have given us the ability to edit the genetic code of living organisms with unprecedented ease. This holds the promise of curing hereditary diseases and creating crops that can survive extreme climates. However, the ability to alter the very blueprint of life brings us into a moral minefield. The most controversial topic is the editing of human embryos-the so-called designer babies. Where do we draw the line between curing a disease and enhancing human traits like intelligence or physical appearance? This could lead to a new form of inequality, where genetic advantages are only available to those who can afford them. Furthermore, the long-term ecological consequences of releasing gene-edited organisms into the wild are unknown. As we play the role of genetic architects, we must proceed with extreme caution and establish a global ethical framework. Innovation in biotechnology is a testament to human ingenuity, but it must be guided by wisdom and a deep respect for the complexity of life.",
    ),
]


TECH_TEXTS["c1"] = [
    (
        "The Ephemeral Nature of Digital Privacy",
        "In the contemporary digital landscape, the notion of privacy has undergone a radical, and some might say irreversible, transformation. We reside in an era where data is frequently characterized as the new oil, a commodity harvested with alarming efficiency by multinational corporations. This phenomenon, often referred to as Surveillance Capitalism, involves the meticulous collection of our digital footprints-every search query, every like, and every geographic movement-to construct predictive models of our behavior. The nuance of this debate lies in the trade-off between bespoke convenience and the subtle erosion of individual autonomy. On one hand, data analytics facilitates a highly personalized user experience, curating content that aligns seamlessly with our aesthetic and intellectual predilections. However, this tailored reality often functions as an echo chamber, reinforcing existing biases and insulating us from dissenting perspectives. Furthermore, the opacity surrounding the processing of these gargantuan datasets leaves the average user in a position of profound vulnerability. When our most intimate preferences become trade secrets, the potential for manipulation, whether for commercial gain or political influence, increases exponentially. It is no longer sufficient to merely opt-out of cookies; we must advocate for robust, transparent legislative frameworks that prioritize the sovereignty of the individual over the bottom line of the tech giants.",
    ),
    (
        "Silicon Valley and the Myth of Meritocracy",
        "For decades, Silicon Valley has cultivated an image of itself as a bastion of pure meritocracy, a place where a brilliant idea and a garage are the only prerequisites for world-altering success. This narrative is undeniably compelling, yet a closer examination reveals a much more stratified and complex reality. While innovation is certainly prized, the trajectory of a startup is often dictated by access to venture capital, social networks, and prestigious academic credentials-resources that are far from equitably distributed. The discourse surrounding disruption frequently masks the fact that many of the most successful tech firms have built their empires on the back of existing public infrastructure and taxpayer-funded research. Moreover, the lack of diversity within the upper echelons of the industry suggests that the merit being rewarded is often synonymous with a very specific, narrow cultural background. As we navigate the ethical minefields of AI and automation, it becomes imperative to dismantle these self-serving myths. A truly innovative society is one that fosters talent from every corner of the community, ensuring that the technology of the future is not merely designed by a small elite, but reflects the diverse needs and aspirations of humanity as a whole.",
    ),
    (
        "The Algorithmic Curation of Human Creativity",
        "The advent of generative AI has sparked a tumultuous debate within the creative industries, raising existential questions about the nature of authorship and the value of human touch. Platforms that can produce intricate paintings or symphonies from a single text prompt are no longer a distant novelty; they are actively reshaping the market for art and music. Critics argue that these models are essentially stochastic parrots, synthesizing vast quantities of human-created data without any genuine understanding or emotional resonance. The danger, from this perspective, is a slow descent into a sea of good enough content-derivative works that prioritize efficiency over the messy, idiosyncratic process of human creation. Conversely, proponents view AI as a sophisticated new medium, a co-pilot that can liberate artists from mundane tasks and push the boundaries of what is possible. The crux of the issue lies in the legal and ethical status of the training data; if an AI is trained on the life's work of thousands of artists without their consent or compensation, is the resulting output a miracle of engineering or a sophisticated form of plagiarism? As we hurtle toward a future where the line between made by hand and generated by code becomes increasingly blurred, we must redefine what we mean by originality in the digital age.",
    ),
    (
        "Quantum Supremacy and the End of Conventional Encryption",
        "The pursuit of quantum supremacy-the point at which a quantum computer can perform a task that is practically impossible for a classical computer-is not merely a milestone in physics; it is a looming crisis for global cybersecurity. Our current cryptographic standards, which safeguard the integrity of everything from personal banking to national defense secrets, are predicated on the mathematical difficulty of factoring large prime numbers. A sufficiently powerful quantum computer, utilizing the principles of superposition and entanglement, could unravel these codes in a matter of seconds. This transition represents a paradigm shift of such magnitude that it necessitates a complete overhaul of our digital security infrastructure. The move toward post-quantum cryptography is a race against time, as hostile actors may already be harvesting encrypted data today with the intention of decrypting it once quantum technology matures. This is a battle fought in the realm of abstract mathematics and extreme cold, yet its consequences will be felt in every corner of the connected world. The challenge is not only technical but logistical; migrating the world's data to new standards is a gargantuan task that requires unprecedented international cooperation and foresight.",
    ),
    (
        "The Paradox of the Smart City: Efficiency vs. Liberty",
        "The Smart City is often presented as a utopian solution to the mounting pressures of urbanization-a high-tech metropolis where sensors, data, and AI converge to optimize everything from traffic flow to energy consumption. In this vision, the city becomes a living organism, capable of responding in real-time to the needs of its inhabitants. However, beneath the veneer of seamless efficiency lies a series of disquieting concerns regarding surveillance and the loss of urban spontaneity. If every street corner is equipped with facial recognition and every movement is tracked to optimize services, does the city still belong to its citizens, or has it become a vast, corporate-managed laboratory? The nuance of the Smart City debate is found in the tension between collective benefit and individual liberty. While a smart grid might significantly reduce a city's carbon footprint, the constant monitoring required to achieve such efficiency can feel like a panopticon. Furthermore, the reliance on proprietary algorithms to manage public services introduces a layer of opacity that can undermine democratic accountability. As we build the cities of the future, we must ensure that smart does not become a euphemism for surveilled, and that the pursuit of efficiency does not come at the expense of the chaotic, vibrant freedom that defines urban life.",
    ),
    (
        "Technological Determinism and the Illusion of Choice",
        "Technological determinism-the theory that technology is the primary driver of social and cultural change-has become a dominant, if often unacknowledged, ideology of our time. We speak of the inevitability of AI, the unstoppable rise of automation, and the natural progression toward a cashless society. This linguistic framing is dangerous because it strips us of our agency, suggesting that we are merely passive passengers on a pre-ordained path toward a digital future. In reality, the direction of technological development is shaped by human choices, policy decisions, and economic incentives. The gig economy, for instance, was not an accidental byproduct of smartphone technology; it was a deliberate business model facilitated by specific legal loopholes and venture capital strategies. By questioning the narrative of inevitability, we can begin to reclaim our role as the architects of our own destiny. We must move beyond the question of what will technology do to us? and start asking what do we want technology to do for us? Reclaiming this agency requires a profound shift in our education and political discourse, moving from a reactive stance to a proactive one that prioritizes human values over technical feasibility.",
    ),
    (
        "The Ethical Imperative of Algorithmic Transparency",
        "As AI systems are increasingly deployed to make life-altering decisions-from determining creditworthiness to assisting in criminal sentencing-the black box problem has moved from a technical curiosity to an ethical imperative. Many of the most advanced machine learning models, particularly deep neural networks, are so complex that even their creators cannot fully explain how they arrive at a specific output. This lack of explainability is profoundly problematic when these systems inherit and amplify the biases present in their training data. If an algorithm systematically discriminates against a specific demographic, but the logic behind the decision is inaccessible, how can the victim seek redress? The nuance here involves the proprietary nature of these algorithms; tech companies often guard their code as trade secrets, arguing that transparency would compromise their competitive advantage or invite gaming of the system. However, in the context of public interest, the right to an explanation must take precedence. We are seeing a burgeoning movement toward Explainable AI, which seeks to create models that are transparent by design. Ultimately, the legitimacy of AI in society depends on our ability to hold these systems accountable to the same standards of fairness and transparency that we demand of human institutions.",
    ),
    (
        "The Neuroplasticity of the Digital Native",
        "The long-term impact of constant digital stimulation on the human brain is a subject of intense scientific scrutiny and societal concern. Digital natives-those born into a world of ubiquitous screens and instant gratification-exhibit patterns of cognitive development that differ markedly from previous generations. On one hand, the ability to rapidly switch between tasks and process complex visual information is heightened. On the other, there is mounting evidence that the constant ping of notifications and the addictive design of social media are eroding our capacity for sustained, deep attention. This is not merely a matter of shortened attention spans; it is a fundamental shift in our neuroplasticity. The shallow reading style encouraged by the internet-skimming for keywords rather than engaging with complex narratives-may be weakening the neural pathways associated with critical thinking and empathy. The nuance of this phenomenon is that the brain is not broken, but is instead adapting to a high-speed, information-dense environment. The challenge for educators and parents is to foster cognitive flexibility-the ability to navigate the digital world effectively while still retaining the capacity for the deep, slow contemplation that is necessary for profound intellectual and emotional growth.",
    ),
    (
        "The Geopolitics of the Semiconductor Industry",
        "In the 21st century, the most critical strategic resource is not oil or gold, but the humble semiconductor. These tiny chips of silicon are the lifeblood of everything from smartphones and medical devices to advanced weapons systems and AI supercomputers. The global supply chain for semiconductors is incredibly fragile and geographically concentrated, with a handful of firms in Taiwan, South Korea, and the United States controlling the vast majority of the world's high-end manufacturing capacity. This concentration has turned the semiconductor industry into a central theater of geopolitical tension. The race to achieve chip sovereignty-the ability to design and manufacture advanced semiconductors domestically-is now a top priority for global superpowers. This is a competition defined by staggering costs; a single modern fabrication plant can cost upwards of 20 billion dollars. Furthermore, the complexity of the manufacturing process, which involves thousands of steps and highly specialized equipment, makes it nearly impossible for any one nation to be entirely self-sufficient. The chip wars are not just about economic dominance; they are about which nations will control the foundational technology of the future and, by extension, the global balance of power.",
    ),
    (
        "Biometric Surveillance and the Body as a Password",
        "The integration of biometric technology into our daily lives-using our fingerprints, irises, and even our gait to unlock devices and access services-is often marketed as the ultimate in security and convenience. After all, your body is a password that you cannot forget and that is seemingly impossible to steal. However, this transition from something you know to something you are introduces a host of permanent and profound risks. Unlike a password or a credit card number, your biometric data cannot be changed if it is compromised. If a database of iris scans or facial maps is breached, the victims are compromised for life. Furthermore, the use of biometrics for mass surveillance in public spaces represents an unprecedented expansion of state and corporate power. The ability to track individuals in real-time, without their consent or knowledge, creates a world where anonymity is a relic of the past. The nuance of the biometric debate is found in the normalization of this technology; we have become so accustomed to Face ID on our phones that we may overlook the broader implications of a world where our bodies are constantly being scanned and cataloged. Protecting the sanctity of our biological identity is perhaps the most personal and pressing civil rights challenge of the digital age.",
    ),
]


TECH_TEXTS["c2"] = [
    (
        "The Silicon Horizon: On the Metaphysics of Post-Humanity",
        "The discourse surrounding the technological singularity-the hypothetical juncture at which technological growth becomes uncontrollable and irreversible-is frequently steeped in a disorienting blend of utopian fervor and existential dread. As we stand on the precipice of unprecedented advancements in quantum computation and neural interfaces, the ontological boundaries between biological life and synthetic intelligence are beginning to blur in a manner that challenges our most fundamental presuppositions regarding consciousness. Is the mind merely an emergent property of intricate calculations that can eventually be replicated on silicon, or is there an ineffable, non-computable quality to human experience that defies digitization? This ambiguity lies at the heart of the modern philosophy of mind. Proponents of transhumanism argue that we are on the verge of a post-human era, where the fusion of carbon and silicon will allow us to transcend our biological limitations, effectively uploading our personalities into vast, indestructible networks. Critics, conversely, warn of a catastrophic loss of human registry, suggesting that a world governed by pure algorithmic logic would be devoid of the empathy, serendipity, and moral friction that define our species. We are not merely discussing faster processors; we are contemplating the potential reconfiguration of the human soul.",
    ),
    (
        "The Ghost in the Code: Algorithmic Bias and the Illusion of Objectivity",
        "There is a pervasive and dangerous myth that algorithms are inherently objective, merely cold mathematical constructs devoid of the messy prejudices that plague human decision-making. However, as AI systems are increasingly integrated into the foundational structures of society-from judicial sentencing to credit allocation-it is becoming clear that these systems often serve as sophisticated vessels for historical bias. The ghost in the code is not a supernatural entity but the reflected image of our own flawed societal datasets. When a machine learning model is trained on decades of data that mirror systemic inequality, it does not correct these errors; it codifies and accelerates them under a veneer of mathematical authority. The nuance of this crisis is found in the opacity of deep learning; when a black box system discriminates, it does so without a discernible rationale, making the path to accountability labyrinthine at best. To dismantle this illusion of objectivity, we must move beyond technical patches and engage in a profound ethical reckoning. We must acknowledge that technology is never neutral; it is an extension of the values, both noble and ignoble, of those who architect it.",
    ),
    (
        "The Panopticon Revisited: Surveillance in the Age of Ubiquitous Data",
        "Foucault's conceptualization of the Panopticon-a prison structure where the few observe the many without being seen-has found its ultimate digital manifestation in the 21st century. Unlike its physical predecessor, the digital panopticon does not require walls; it is woven into the very fabric of our social and commercial interactions. We are participants in a grand bargain where we relinquish the sanctity of our private lives in exchange for the frictionless convenience of the cloud. Every interaction is harvested, every sentiment analyzed, and every movement cataloged in the service of what has been termed behavioral futures. The danger here is not merely the loss of privacy, but the subtle manipulation of human agency. When algorithms can predict our desires before we even articulate them, the boundary between free will and programmed response begins to erode. This is a quiet revolution, a soft authoritarianism that operates not through coercion, but through the seductive allure of personalized experience. The challenge of our era is to reclaim the right to be unobserved, to protect the chaotic, unquantifiable interiority of the human spirit in a world that seeks to turn every soul into a data point.",
    ),
    (
        "The Semiconductor Hegemony: Silicon as the New Geopolitical Fault Line",
        "In the grand theater of contemporary geopolitics, the most potent weapon is not the ballistic missile, but the nanometer-scale transistor. The global hierarchy of power is increasingly dictated by the control of semiconductor manufacturing-a process of such staggering complexity and astronomical cost that it creates a natural monopoly for a handful of geographic enclaves. This silicon hegemony has turned the supply chain into a battlefield of strategic denial and technological containment. The race for chip sovereignty is not merely an economic competition; it is an existential struggle to control the foundational layer of modern civilization. From the guidance systems of autonomous weapons to the vast server farms powering artificial general intelligence, everything rests on the integrity of this fragile supply chain. The irony of our age is that our most advanced aspirations are tethered to a handful of fabrication plants located in some of the world's most volatile regions. The geopolitical friction of the future will be defined by the flow of silicon, and the nations that fail to secure their place in this high-tech ecosystem risk a slow descent into technological irrelevance.",
    ),
    (
        "The Aesthetics of the Synthetic: Art in the Age of Generative AI",
        "The intrusion of generative AI into the creative arts has provoked a tumultuous aesthetic and ontological crisis. When a neural network can synthesize a Rembrandt or a Bach with indistinguishable fidelity, we are forced to confront the question: what remains of the aura of the original work of art? Benjamin's lament regarding mechanical reproduction is amplified a thousandfold by digital generation. Critics argue that AI art is essentially a form of sophisticated plagiarism-a parasitic extraction of human labor that replaces the arduous, embodied process of creation with an instantaneous, stochastic output. However, a more nuanced view suggests that AI is a new camera for the mind, a medium that allows for the exploration of latent spaces previously inaccessible to the human imagination. The ambiguity lies in the locus of creativity: is the artist the one who codes the algorithm, the one who crafts the prompt, or is the machine itself an autonomous agent? As we navigate this landscape, we must redefine the value of art. Perhaps the value will shift away from the final product and return to the intent, the struggle, and the inimitable human context that a machine, however intelligent, can never truly possess.",
    ),
    (
        "The Neuroplasticity of the Hyperconnected Mind",
        "We are the subjects of a vast, uncontrolled experiment in cognitive reconfiguration. The digital native is not merely a social category; it is a neurobiological reality. The constant, high-frequency stimulation of the digital environment is rewriting the circuitry of the human brain, prioritizing rapid information processing and task-switching over the slow, deep contemplative modes that have historically fueled profound intellectual achievement. There is a growing concern that we are losing our capacity for deep reading and sustained focus-the very skills required to navigate the complexities of our age. The nuance of this shift is that the brain is not deteriorating; it is adapting with remarkable plasticity to an information-dense, distraction-rich landscape. We are becoming masters of the surface, capable of navigating vast oceans of data with incredible speed, yet we risk losing the ability to dive into the depths. The challenge for future generations will be to maintain a bilingual cognitive capacity: the ability to thrive in the hyperconnected present while retaining the ancient, essential power of quiet, solitary reflection.",
    ),
    (
        "The Quantum Leap: Cryptography and the End of Digital Trust",
        "The quest for quantum supremacy is frequently framed as a triumph of physics, yet its most immediate consequence will be the total annihilation of the current foundations of digital trust. Our entire global economy, from the confidentiality of diplomatic cables to the security of the blockchain, is predicated on the mathematical difficulty of factoring large integers-a task that a quantum computer could perform with trivial ease. This transition represents a paradigm shift of such magnitude that it threatens to render the digital history of the last thirty years an open book. The frantic move toward post-quantum cryptography is a desperate attempt to build new locks before the old ones are shattered. The ambiguity of this era is that we may already be living in a state of compromised security; hostile actors may be harvesting encrypted data today with the intent of decrypting it a decade from now. This store now, decrypt later strategy means that the secrets of the present are already vulnerable to the technology of the future. The quantum leap is not just a forward movement; it is an unraveling of the digital past.",
    ),
    (
        "The Paradox of Automation: Labor and the Search for Meaning",
        "The Fourth Industrial Revolution is characterized by a paradox: the more we automate labor, the more we are forced to confront the question of human purpose. For centuries, the work ethic has been the central organizing principle of social and individual identity. As AI and robotics begin to displace not just manual labor but the cognitive work of the middle class, we face an existential void. If a machine can diagnose a disease, write a legal brief, or manage a project more efficiently than a human, what becomes of the dignity of work? The nuance of this debate is found in the tension between economic efficiency and social stability. Proponents of a Universal Basic Income argue that we must decouple income from labor to survive an automated future. However, income is not the same as meaning. The challenge of an automated society is not just the distribution of wealth, but the distribution of purpose. We must find new ways to value human contribution that go beyond the narrow metrics of productivity, or risk a future defined by a profound and widespread crisis of identity.",
    ),
    (
        "Biometric Sovereignty and the Sanctity of the Biological Self",
        "The transition from knowledge-based security, such as passwords, to being-based security, such as biometrics, represents the final enclosure of the human body by the digital apparatus. When your fingerprint, your iris, or your gait becomes your password, you are no longer a user of technology; you are a component of it. The convenience of Face ID masks a profound loss of biometric sovereignty. Unlike a password, a biometric marker cannot be changed if it is leaked. If your facial map is compromised, it is compromised for life. Furthermore, the normalization of biometric scanning in public and private spaces creates a world where anonymity is not just difficult, but impossible. We are moving toward a state of permanent visibility, where our biological selves are constantly being cataloged and cross-referenced by opaque algorithms. The challenge of the 21st century is to establish a new category of civil rights: the right to biometric privacy, the right to exist in the world without being a barcode. We must protect the sanctity of the biological self before it is completely subsumed by the digital panopticon.",
    ),
    (
        "The Epistemological Crisis: Deepfakes and the Death of Evidence",
        "We are entering an era of epistemic fragmentation, where the very concept of objective truth is being eroded by the arrival of high-fidelity synthetic media. Deepfakes-AI-generated audio and video that are indistinguishable from reality-represent the ultimate weapon of disinformation. When we can no longer trust the evidence of our own eyes and ears, the foundations of democratic discourse begin to crumble. The danger is not just that we will believe lies, but that we will cease to believe in the truth. This is the liar's dividend: a world where a politician can dismiss a real recording of their misconduct as a fake, and a skeptical public has no way to verify the claim. The nuance of this crisis is that it cannot be solved with better technology alone; every detection algorithm is eventually bypassed by a better generation of AI. The solution must be cultural and educational. We must foster a new kind of radical skepticism and a return to trusted institutional hierarchies of evidence. Without a shared reality, a society cannot function; the death of evidence is the birth of chaos.",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, estruturas repetitivas e vocabulario concreto",
    "a1": "verbos basicos, conectores simples e rotina tecnologica",
    "a2": "passado simples, comparacoes e narrativas curtas",
    "b1": "opinioes, causa e consequencia, vocabulario intermediario",
    "b2": "argumentacao, ideias abstratas e vocabulario avancado",
    "c1": "nuance, estilo, opinioes complexas e estruturas variadas",
    "c2": "texto refinado, inferencia, ambiguidade e registros variados",
}


class Command(BaseCommand):
    help = "Replace the Tecnologia catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="tecnologia")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = TECH_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-tecnologia-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Tecnologia texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre tecnologia: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D cartoon style, clean lines, high quality, "
            f"educational technology scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
