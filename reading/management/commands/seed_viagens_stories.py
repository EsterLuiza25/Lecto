import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


TRAVEL_TEXTS = {
    "iniciante": [
        (
            "The Big Blue Suitcase",
            "Leo has a big blue suitcase. The suitcase is on the floor. Leo puts a green shirt in the suitcase. He puts blue jeans in the suitcase. Leo is happy. He is ready for a trip. The suitcase is heavy now. Leo closes the suitcase. He is a traveler. Traveling is fun for Leo.",
        ),
        (
            "A Day at the Beach",
            "The sun is hot today. Anna is at the beach. The sand is yellow and soft. The ocean is big and blue. Anna has a red umbrella. She sits under the umbrella. She looks at the water. A small boat is near. Anna is calm. The beach is a beautiful place for a trip.",
        ),
        (
            "The Red Passport",
            "Sara has a red passport. The passport is in her hand. Sara is at the airport. She looks at her passport. She looks at her ticket. The airport is very big. Sara walks to the gate. She is excited. Her passport is important. Sara is ready for a new country today.",
        ),
        (
            "The Green Map",
            "The map is on the table. It is a green and white map. Tom looks at the map. He sees a mountain. He sees a river. Tom points to a small city. He wants to go there. The map is very helpful. Tom plans a journey. He is a curious traveler. The map shows the way.",
        ),
        (
            "A Walk in the Park",
            "The park is in the city. It is a quiet park. Many trees are green. A small path is near the flowers. Paul walks on the path. He has a camera. He takes a photo of a bird. The bird is small and yellow. Paul is happy in the park. Nature is good for a trip.",
        ),
        (
            "The Fast Train",
            "The train is at the station. It is a long, silver train. The train is very fast. Marta sits near the window. She looks at the trees. She looks at the houses. The train moves quickly. Marta has a bag and a book. The journey is short. Marta arrives in the city soon.",
        ),
        (
            "The Yellow Taxi",
            "A yellow taxi is in the street. The taxi is near the hotel. John enters the taxi. He has a small bag. The driver is kind. The taxi moves in the city traffic. John looks at the tall buildings. The taxi stops at the airport. John pays the driver. The taxi is a fast way to travel.",
        ),
        (
            "The Small Hotel Room",
            "The hotel room is small and clean. The bed is white and soft. There is a window in the room. The window shows a quiet street. A lamp is on the table. Maria puts her bag on the chair. She is tired from the trip. Maria sleeps in the soft bed. The hotel is welcoming.",
        ),
        (
            "A Flight to the Clouds",
            "The airplane is in the sky. It is a white airplane. Lucas looks out the window. He sees white clouds. The sun is bright above the clouds. The airplane is very high. Lucas is calm. He listens to music. The flight is long. Lucas likes to see the world from the sky.",
        ),
        (
            "The City Bus",
            "The city bus is red and white. Many people are on the bus. The bus stops at the museum. A tourist gets off the bus. The museum is a big building. The bus moves again. It stops at the park. The bus is a cheap way to see the city. The journey is interesting today.",
        ),
    ],
    "a1": [
        (
            "Packing for a Summer Vacation",
            "Next week, my family is going on a summer vacation to the beach. Today, I am very busy because I need to pack my suitcase. First, I put my swimsuit and my sunglasses in the bag. Then, I add some light clothes and a pair of comfortable sandals. My mother tells me not to forget the sunscreen because the sun is very strong. I also pack a book to read during the flight. I am very excited about this trip because I love the ocean. We are ready for a great adventure together.",
        ),
        (
            "At the Busy Train Station",
            "I am at the central train station in London. The station is very large and crowded with many travelers. I look at the big digital board to find my platform. My train to Paris leaves at ten o'clock. I have a small backpack and a cup of hot coffee. I wait on the platform for ten minutes. Suddenly, I see the silver train arriving. It is very long and modern. I find my seat near the window because I like to look at the countryside. Traveling by train is fast and very comfortable.",
        ),
        (
            "A Visit to a Famous Museum",
            "Today, we are visiting a famous art museum in Paris. We wait in a short line to buy our tickets. Inside, the building is beautiful and very quiet. We see many old paintings and statues from different countries. My favorite part is the room with the large landscape paintings. I use my camera to take photos, but I do not use the flash. After the tour, we go to the museum cafe. I drink a cold juice and write a postcard to my grandmother. It is a very interesting day.",
        ),
        (
            "My First Hotel Experience",
            "Last night, I stayed in a hotel for the first time. The hotel is near the city center and it is very tall. My room was on the fifth floor. Inside, the bed was very soft and the towels were white and clean. There was a small television and a desk near the window. In the morning, I went to the dining room for breakfast. I ate some fresh fruit, eggs, and toast. The staff was very friendly and helped me with my bags. Staying in a hotel is a very nice experience.",
        ),
        (
            "Exploring a Local Market",
            "When I travel to a new city, I always visit the local market. This morning, I am at a market in Mexico. The place is full of colors and different smells. There are many stalls with fresh vegetables and exotic fruits. I buy a bag of sweet mangoes and a handmade hat. People are very loud because they are selling their products. I like the market because it is a great place to see the local culture. Everything is very cheap and the food is delicious.",
        ),
        (
            "A Long Flight Across the Ocean",
            "I am on a plane from Brazil to Portugal. The flight is very long, about ten hours. I sit in my seat and put on my seatbelt. A flight attendant gives me a pillow and a blanket. During the flight, I watch two movies on the small screen in front of me. I also eat a meal with chicken, rice, and salad. Looking out the window, I see the dark ocean and the stars. I try to sleep because I want to have energy tomorrow. Flying is a fast way to see the world.",
        ),
        (
            "Walking in the Mountains",
            "This weekend, my friends and I are hiking in the mountains. We wear heavy boots and carry backpacks with water and snacks. The path is steep, but the air is very fresh and clean. We see many tall trees and a small waterfall. We stop near a river to eat our lunch. The view from the top is amazing because we can see the whole valley. I take many photos of the mountains with my phone. We are tired at the end of the day, but we are very happy.",
        ),
        (
            "Sending a Postcard from Italy",
            "I am having a wonderful time in Rome. Every day, I visit old buildings and eat delicious pasta. Today, I am at a small shop to buy postcards. I choose a beautiful card with a photo of the Colosseum. I sit at a table in the square and write a message to my best friend. I tell him about the sunny weather and the friendly people. Then, I go to the post office to buy a stamp. Sending a postcard is a traditional way to share my travel memories with my family.",
        ),
        (
            "Taking a City Tour Bus",
            "To see the city quickly, I take a red double-decker tour bus. I sit on the top floor because the view is better. The bus travels past the big cathedral, the old bridge, and the central park. I listen to a recording in English that explains the history of the buildings. I can get off the bus at any stop and get on again later. It is a very convenient way for tourists to explore the city. I see many interesting places today and I take many notes in my diary.",
        ),
        (
            "Planning a Trip with a Friend",
            "My friend Lucas and I are planning a trip for next summer. We sit at a cafe with our laptops and a big paper map. We want to visit three different countries in South America. First, we look for cheap flights and hotels online. We also read travel blogs to find the best places to eat. Lucas wants to visit the mountains, but I prefer the historic cities. We talk about our budget and the things we need to buy. Planning a trip is a lot of work, but it is very exciting.",
        ),
    ],
    "a2": [
        (
            "A Backpacking Trip Through Europe",
            "Last summer, my friend Lucas and I decided to go backpacking through Europe for three weeks. We visited three different countries: Portugal, Spain, and France. In the past, I always traveled with my parents in comfortable hotels, but this trip was much more adventurous. We stayed in small hostels and met many interesting travelers from all over the world. Our favorite city was Barcelona because the architecture was more beautiful than anything I saw before. We spent hours walking through the narrow streets and eating delicious tapas near the beach. However, traveling with a heavy backpack was more difficult than I expected. My shoulders were very tired at the end of every day! Despite the hard work, I think that backpacking is a better way to see the world because you feel more free. It was an unforgettable experience that taught me how to be more independent.",
        ),
        (
            "My First Visit to the Grand Canyon",
            "Two years ago, my family traveled to the United States to visit the Grand Canyon in Arizona. I remember looking at photos online before the trip, but seeing it in person was completely different. The canyon is much larger and deeper than it looks in pictures. We arrived early in the morning to watch the sunrise, and the colors of the rocks changed from dark purple to bright orange. It was the most beautiful scene I ever saw. We hiked down a small path for two hours, which was easier than climbing back up! The air was very dry, so we drank a lot of water. My younger sister was a bit scared of the height, but my father helped her feel safe. We spent the whole day exploring and taking photos. That trip showed me that nature is more powerful and magnificent than any city building.",
        ),
        (
            "A Weekend in a Brazilian Colonial Town",
            "Last month, I went to Ouro Preto, a famous colonial town in Minas Gerais, Brazil. The city is very different from Brasilia because it has many steep hills and old stone streets. In Brasilia, the buildings are modern and the streets are wide, but in Ouro Preto, everything feels like a trip back to the eighteenth century. I visited several historic churches with beautiful golden decorations. The weather was a bit colder than I expected, so I wore a heavy jacket in the evening. I also tried pao de queijo and traditional mineiro food, which was more delicious than the food in my home city. Walking up the hills was very tiring, but the view from the top of the mountains was worth the effort. It was a wonderful journey that helped me understand more about Brazilian history and culture.",
        ),
        (
            "Lost in the Streets of Tokyo",
            "During my vacation last year, I traveled to Tokyo, Japan. It is the largest and most crowded city I ever visited. On my second day, I decided to explore the Shibuya district alone. Everything was very exciting, but I quickly realized that I was lost! The street signs were more difficult to read than I thought, and there were thousands of people everywhere. I tried to use the GPS on my phone, but the signal was weak between the tall buildings. Finally, I went into a small convenience store and asked for help. The shop assistant was very kind and showed me the way to the nearest subway station. Even though I was a confused tourist, I felt very safe because the city is extremely organized. That day taught me that getting lost is sometimes a great way to discover small, hidden shops and cafes.",
        ),
        (
            "A Rainy Adventure in London",
            "I spent my winter break in London, and it was a very rainy adventure! Everyone told me that London is rainier than Brasilia, and they were right. I carried my umbrella every day, but sometimes the wind was too strong to use it. One afternoon, I visited the British Museum to escape a heavy storm. The museum is so big that you need more than one day to see everything. I saw the Egyptian mummies and the Rosetta Stone, which was more interesting than my history books at school. Later, I took a red bus to see the Big Ben, but it was covered in fog. Despite the grey weather, the city felt very cozy and lively. I drank a lot of hot tea in small cafes to stay warm. I prefer sunny weather, but London has a special charm even when it is raining.",
        ),
        (
            "Camping Under the Stars",
            "Last weekend, my cousins and I went camping in a national park near my city. In the past, we always stayed in hotels with air conditioning, so sleeping in a tent was a new experience. We arrived at the campsite in the afternoon and worked together to build our tents. It was more complicated than it looked in the instruction manual! In the evening, we made a small fire and cooked sausages and marshmallows. The sky was much clearer than in the city, and we could see thousands of stars. It was quieter and more peaceful than my neighborhood at home. However, the ground was harder than my bed, and I didn't sleep very well. In the morning, we woke up with the sound of birds and drank coffee outdoors. It was a simple trip, but it was better than staying home watching TV.",
        ),
        (
            "A Boat Trip in the Amazon Rainforest",
            "Five years ago, I took a boat trip along the Amazon River in northern Brazil. It was the most exotic journey of my life. The boat was our home for three days, and we slept in hammocks on the deck. It was more humid and hotter than the South of Brazil, where I live. Every morning, I watched the pink dolphins jumping in the water near the boat. We also visited a small indigenous village and learned how they use plants from the forest for medicine. The forest is so dense and green that it feels like a different planet. At night, the sounds of the animals were louder than the traffic in a big city. It was a bit scary at first, but then it became very relaxing. This trip made me realize that we must protect the rainforest because it is a unique treasure.",
        ),
        (
            "Learning to Ski in the Andes",
            "Last July, I traveled to Chile to see the snow for the first time. My goal was to learn how to ski in the Andes Mountains. I thought skiing would be easier than skating, but I was wrong! On my first day, I fell down many times and my legs felt very heavy. The instructor was more patient than I was with myself. By the third day, I could move down a small hill without falling. The mountains were much higher and whiter than any mountain in Brazil. The air was very thin, so I felt tired more quickly than usual. After the lessons, I drank hot chocolate with my new friends from Argentina. Even though my body was sore, I felt very happy because I learned a new skill. It was a cold but very exciting vacation.",
        ),
        (
            "A Flight Delay in New York",
            "My trip to New York last winter started with a big problem: a flight delay. I was at the airport in Sao Paulo when the airline announced that my flight was eight hours late because of a snowstorm in the US. I was more frustrated than the other passengers because I wanted to arrive early to see the Christmas lights. I spent the whole afternoon sitting on the floor near a power outlet to charge my phone. I read a whole book and talked to a traveler from Mexico who was also waiting. When the plane finally arrived, I was very tired. The flight was longer than usual because of the strong wind. However, when I finally arrived in Manhattan and saw the snow, I forgot all my problems. The delay was annoying, but the trip was still wonderful.",
        ),
        (
            "Biking through Amsterdam",
            "Amsterdam is the most bike-friendly city I ever visited. Last spring, I decided to rent a bicycle to explore the canals and parks. Biking in Amsterdam is much faster and more popular than driving a car. There are more bicycles than people in the city! At first, I was a bit nervous because the local bikers are very fast and disciplined. I had to pay more attention to the traffic than I do when I am walking. I biked to the Van Gogh Museum and then to a large park called Vondelpark. The city is very flat, so biking was not as tiring as I expected. The weather was perfect-not too hot and not too cold. It was a healthy and fun way to see the historic buildings and the beautiful flowers. I think every city should be more like Amsterdam.",
        ),
    ],
    "b1": [
        (
            "The Rise of Sustainable Tourism",
            "In recent years, the concept of sustainable tourism has become increasingly popular among travelers who are concerned about the environment. This shift is happening because many famous destinations, such as Venice or the Maya Bay in Thailand, have suffered from the negative consequences of overtourism. Consequently, local governments are now implementing stricter rules to protect their natural and cultural heritage. For example, some cities are limiting the number of visitors per day or banning large cruise ships. In my opinion, this is a necessary step to ensure that future generations can still enjoy these beautiful places. Furthermore, being a sustainable traveler involves choosing local businesses instead of international chains. By staying in family-owned guest houses and eating at local markets, tourists can contribute directly to the local economy. Although it might require more planning and sometimes a higher budget, the long-term benefits for the planet and the communities are undeniable. Therefore, we should all try to travel more consciously and respect the places we visit.",
        ),
        (
            "The Benefits of Solo Traveling",
            "Many people feel anxious about the idea of traveling alone, but solo traveling can be one of the most rewarding experiences of your life. One primary advantage is the complete freedom it offers; you don't have to negotiate your itinerary or compromise on your budget with anyone else. Consequently, you can wake up whenever you want and change your plans at the last minute without any stress. Furthermore, when you travel alone, you are more likely to interact with local people and other travelers. Because you don't have a companion to talk to, you become more approachable and observant of your surroundings. However, solo travel also requires a high level of responsibility and safety awareness. Since you are the only one in charge, you must be very organized with your documents and navigation. In my view, everyone should try to take at least one solo trip in their lifetime. It helps you build confidence and learn how to solve problems independently, which are essential skills for personal growth.",
        ),
        (
            "Digital Nomads: Working While Traveling",
            "The dream of working from a beach in Bali or a cozy cafe in Lisbon has become a reality for thousands of people known as digital nomads. This lifestyle has emerged due to the rapid advancement of communication technology and the increasing flexibility of remote work. Because all they need is a laptop and a stable internet connection, digital nomads can explore the world without quitting their jobs. However, this lifestyle is not as easy as it looks on social media. One major challenge is maintaining a productive work-life balance while being in an exciting new environment. Consequently, many nomads struggle with burnout or loneliness after moving to different cities every month. In addition, navigating visas and local taxes can be quite complicated. Despite these drawbacks, the ability to immerse yourself in different cultures while maintaining a professional career is an incredible opportunity. In conclusion, being a digital nomad requires great discipline and planning, but the cultural enrichment you gain is definitely worth the effort.",
        ),
        (
            "The Importance of Travel Insurance",
            "Many travelers tend to ignore travel insurance because they think it is an unnecessary expense. However, a single medical emergency or a canceled flight can quickly turn a dream vacation into a financial nightmare. The primary purpose of insurance is to provide a safety net when things go wrong unexpectedly. For instance, if you get sick in a country with high healthcare costs, the insurance will cover your bills, which can save you thousands of dollars. Furthermore, most policies also protect you against lost luggage or theft. Consequently, you can enjoy your trip with much more peace of mind. Although it might seem like a waste of money if you don't end up using it, the risk of traveling without protection is simply too high. In my opinion, if you can afford to travel, you can afford travel insurance. It is a small price to pay for the security of knowing that you are covered in case of an emergency. Therefore, always make sure to read the fine print and choose a policy that fits your specific needs.",
        ),
        (
            "Cultural Shock and How to Overcome It",
            "When you travel to a country with a very different culture from your own, it is common to experience what we call culture shock. This usually happens because the social norms, food, and language are unfamiliar, which can make you feel frustrated or isolated. For example, a traveler from Brazil might find the social etiquette in Japan quite complex and different. One way to overcome this is by doing research before you arrive. By learning a few basic phrases and understanding local customs, you show respect and make your daily interactions much smoother. Furthermore, it is important to keep an open mind and avoid making constant comparisons with your home country. Instead of focusing on what is strange, try to see the differences as an opportunity to learn something new. Consequently, you will feel more integrated and your travel experience will be much richer. In the end, culture shock is a natural part of the journey that eventually leads to a broader perspective of the world.",
        ),
        (
            "The Evolution of Low-Cost Airlines",
            "Low-cost airlines have completely transformed the way we travel, making international trips accessible to millions of people who couldn't afford them before. This change occurred because these airlines found ways to reduce their operational costs, such as using secondary airports and charging for extra services like luggage and seat selection. Consequently, a flight across Europe or Asia can now be cheaper than a train ticket. However, there are some downsides to this business model. Because these tickets are so cheap, the planes are often very crowded and the customer service can be quite limited. Furthermore, the distance between secondary airports and the city centers can lead to higher transportation costs once you land. In my view, low-cost airlines are great for short trips or budget travelers, but you must be very careful with the extra fees. Always calculate the total cost, including transportation and bags, before you decide that a ticket is truly a bargain.",
        ),
        (
            "Why We Should Support Local Tourism",
            "During the last global crisis, many people rediscovered the beauty of their own countries because international borders were closed. This trend, known as local tourism or staycations, has many positive consequences for both the traveler and the community. First of all, traveling locally is usually more affordable and has a smaller carbon footprint because you don't need to take long-haul flights. Furthermore, it allows you to discover hidden gems and historical sites that you might have ignored in the past. From a social perspective, supporting local tourism is vital for small businesses that rely on visitors to survive. When you visit a nearby town, you are helping to preserve its traditions and economy. In my opinion, we often forget that adventure can be found just a few hours away from our homes. Therefore, instead of always dreaming of distant lands, we should also appreciate and invest in the wonders that our own regions have to offer.",
        ),
        (
            "The Magic of Slow Travel",
            "In a world that is always in a hurry, slow travel is a movement that encourages people to spend more time in fewer places. Instead of trying to visit five cities in ten days, slow travelers might spend two weeks in a single village. The main reason for this approach is the desire for a deeper connection with the local culture. Because you stay longer, you can develop a routine, meet your neighbors, and discover the best local spots that are not in the guidebooks. Consequently, your trip becomes more relaxing and less like a checklist of tourist attractions. Furthermore, slow travel is often more sustainable and cheaper because you save money on transportation and can rent apartments with kitchens. In my view, traveling shouldn't be about how many stamps you have in your passport, but about the quality of the memories you create. If you slow down, you will see things that most tourists miss, and your journey will be much more meaningful.",
        ),
        (
            "Language Learning Through Travel",
            "One of the best ways to improve your English, or any other language, is by traveling to a country where it is spoken. This is effective because you are forced to use the language in real-life situations, such as ordering food, asking for directions, or chatting with locals. Unlike a classroom, the real world provides an immersive environment where you hear different accents and slang every day. Furthermore, the necessity of being understood motivates you to study harder and overcome your fear of making mistakes. Consequently, your listening and speaking skills improve much faster than they would at home. However, you must make an effort to step out of your comfort zone. If you only hang out with people from your own country, you won't practice as much. In conclusion, travel is the ultimate language school. It doesn't just teach you grammar and vocabulary; it gives you the confidence to communicate with people from all walks of life.",
        ),
        (
            "Traveling with Kids: Challenges and Rewards",
            "Traveling with children requires a lot of extra planning, but it is a wonderful way to broaden their horizons from a young age. One major challenge is the logistics; you have to pack more things and choose destinations that are safe and entertaining for kids. Furthermore, children can get tired or bored during long flights, which can be stressful for the parents. Consequently, it is important to include plenty of breaks and kid-friendly activities in your itinerary. Despite the hard work, the rewards are immense. Children are naturally curious and often notice small details that adults overlook. Seeing a new culture through a child's eyes can make the parents appreciate the world in a different way. Moreover, it teaches children to be more flexible and tolerant of differences. In my opinion, the memories created during a family trip are priceless and help build a strong bond. With a little bit of patience and a good sense of humor, traveling with kids can be a life-changing adventure for the whole family.",
        ),
    ],
    "b2": [
        (
            "The Gentrification of Historic Neighborhoods",
            "The phenomenon of gentrification in historic city centers has become a contentious issue in the global travel industry. As picturesque neighborhoods in cities like Lisbon or Barcelona become social media sensations, they attract a massive influx of tourists and investors. While this often leads to the renovation of crumbling buildings and an increase in local tax revenue, it frequently comes at a steep social cost. Long-term residents are often priced out of their own communities as traditional apartments are converted into short-term holiday rentals. Consequently, the authentic soul of the neighborhood-its local bakeries, craft workshops, and generational residents-begins to vanish, replaced by a sanitized version of culture designed for consumption. In my view, finding a balance between urban revitalization and the preservation of community life is the greatest challenge for modern urban planning. Travelers must be mindful of their impact and seek out ways to support the original fabric of the places they visit, rather than just chasing the perfect photo for their feed.",
        ),
        (
            "The Philosophy of the Slow Travel Movement",
            "In an era dominated by rapid transportation and bucket-list tourism, the slow travel movement offers a profound philosophical alternative. Instead of treating travel as a series of boxes to be checked, slow travel encourages individuals to immerse themselves deeply in a single location, prioritizing quality of experience over quantity of destinations. This approach is rooted in the belief that true discovery requires time, patience, and a willingness to step off the beaten path. When you spend a month in a remote village rather than a weekend in a capital city, your relationship with the environment changes fundamentally. You begin to understand the subtle nuances of the local dialect, the rhythms of the daily market, and the unspoken social codes of the community. Furthermore, slow travel is inherently more sustainable, as it reduces the carbon footprint associated with frequent flights and long-distance commutes. Ultimately, it is an invitation to reclaim our time and reconnect with the world in a way that is both meaningful and ecologically responsible.",
        ),
        (
            "Voluntourism: A Double-Edged Sword?",
            "Voluntourism-the practice of combining international travel with volunteer work-is often marketed as a noble way to give back to the world. However, it has increasingly come under scrutiny for its potential unintended consequences. While many participants are driven by a genuine desire to help, the short-term nature of these projects can sometimes do more harm than good. For instance, unskilled volunteers working in orphanages or construction sites may displace local workers or provide inconsistent care to vulnerable populations. Furthermore, the focus often shifts from the needs of the community to the transformative experience of the traveler. To truly make a difference, volunteer programs must be community-led and focused on long-term sustainability rather than quick fixes. Prospective voluntourists should rigorously vet organizations to ensure that their presence is actually beneficial and doesn't just reinforce paternalistic stereotypes. When done correctly, it can be a powerful tool for global solidarity, but it requires a high degree of ethical awareness and humility.",
        ),
        (
            "The Future of Air Travel in a Warming World",
            "As the global community grapples with the climate crisis, the aviation industry faces an existential challenge. Air travel is one of the fastest-growing sources of greenhouse gas emissions, yet for many, it remains an indispensable part of modern life and global commerce. The emergence of flight shaming in some cultures reflects a growing awareness of the individual carbon footprint associated with long-haul journeys. In response, aerospace engineers are racing to develop sustainable aviation fuels, electric aircraft, and even hydrogen-powered engines. However, these technologies are still in their infancy and face significant regulatory and logistical hurdles. In the meantime, some argue that we must drastically reduce the frequency of our flights and embrace alternative modes of transport, such as high-speed rail. The debate boils down to a fundamental question: can we maintain our global connectivity without compromising the stability of our planet's climate? The answer will likely require a combination of radical technological innovation and a major shift in our cultural expectations regarding travel.",
        ),
        (
            "The Digital Nomad and the Erosion of Local Identity",
            "The rise of the digital nomad has undoubtedly redefined the concept of the workplace, offering unprecedented freedom to those with the right skills. However, the presence of large communities of remote workers in developing nations can have complex effects on local identities. In cities like Medellin or Chiang Mai, the influx of high-earning foreigners can drive up the cost of living, creating a digital divide between the nomads and the local population. While these travelers bring capital and technical skills, they often live in expat bubbles, interacting primarily with other foreigners and utilizing services tailored to Western tastes. This can lead to a homogenization of culture, where local businesses are replaced by trendy coworking spaces and avocado-toast cafes. To mitigate these effects, digital nomads should strive for deeper integration, learning the local language and contributing to the community in ways that transcend mere consumption. True nomadism should be an exchange of ideas and cultures, not just a search for the cheapest cost of living.",
        ),
        (
            "Dark Tourism: Exploring the Sites of Tragedy",
            "Dark tourism-visiting sites associated with death, tragedy, or historical suffering-has become a significant niche in the travel industry. From the killing fields of Cambodia to the ruins of Chernobyl, millions of people are drawn to places that witnessed humanity's darkest moments. While some argue that these visits can be morbid or exploitative, others believe they serve a vital educational and commemorative purpose. When approached with respect and historical context, visiting a site of tragedy can foster deep empathy and a commitment to ensuring that such events never happen again. However, the commodification of these sites-such as selling souvenirs or taking disrespectful selfies-is a major ethical concern. Managing dark tourism requires a delicate balance between preserving the solemnity of the location and providing the necessary infrastructure for visitors. Ultimately, the value of dark tourism lies in its ability to force us to confront the complexities of our history and reflect on the fragility of our civilization.",
        ),
        (
            "The Impact of Language on the Travel Experience",
            "Language is far more than just a tool for communication; it is a gateway to the soul of a culture. While English has undoubtedly become the global lingua franca of travel, relying solely on it can limit the depth of one's experience. When you make the effort to learn even the basics of a local language, you signal a level of respect and curiosity that is almost always reciprocated. It breaks down the invisible barrier between tourist and local, allowing for more authentic and spontaneous interactions. Furthermore, language shapes how we perceive the world; certain concepts or emotions can only be fully expressed through specific linguistic structures. For instance, the Portuguese word saudade or the Japanese komorebi offer windows into unique cultural temperaments. Travelers who embrace linguistic diversity often find that their journeys are richer and more nuanced. In the age of instant translation apps, the human effort of learning a language remains an irreplaceable bridge between diverse worldviews.",
        ),
        (
            "Navigation in the Age of Algorithms",
            "In the past, traveling required a high degree of navigational skill, involving paper maps, compasses, and the frequent need to ask strangers for directions. Today, our journeys are increasingly mediated by sophisticated algorithms and GPS technology. While this has made travel infinitely more convenient and reduced the anxiety of getting lost, it has also changed how we perceive space. When we follow a blue dot on a screen, we often become less aware of our physical surroundings, focusing on the destination rather than the journey itself. We lose the serendipity of accidental discoveries-the hidden alleyway or the local shop that isn't listed on a digital map. Furthermore, these algorithms often funnel travelers toward the same highly rated locations, contributing to the overcrowding of popular spots. To truly experience a place, we must occasionally intentionally unplug and allow ourselves to wander aimlessly. Reclaiming our sense of direction is a way of reclaiming our autonomy as explorers in an increasingly programmed world.",
        ),
        (
            "The Ethical Dilemma of Animal Tourism",
            "From elephant trekking in Southeast Asia to swimming with dolphins in the Caribbean, animal-related attractions have long been a staple of international tourism. However, growing awareness of animal welfare has led to a major reevaluation of these practices. Many of these experiences involve the capture, confinement, and often cruel training of wild animals for human entertainment. While these activities can provide income for local communities, the ethical cost is increasingly seen as unacceptable. Consequently, many travel agencies are now boycotting attractions that involve captive wildlife and promoting ethical sanctuaries instead. The challenge for travelers is to distinguish between genuine conservation efforts and greenwashed businesses that use animals for profit. Ethical animal tourism should focus on observing animals in their natural habitats from a distance, with minimal interference. As our understanding of animal sentience evolves, the travel industry must transition toward a more compassionate and respectful relationship with the natural world.",
        ),
        (
            "Travel as a Catalyst for Personal Growth",
            "It is a common cliche that travel broadens the mind, but the underlying psychological truth is far more complex. Travel serves as a powerful catalyst for personal growth because it forces us out of our comfort zones and challenges our most basic assumptions about the world. When we are confronted with different ways of living, eating, and thinking, we are essentially performing a reset on our internal maps. This cognitive flexibility is a key component of creativity and problem-solving. Furthermore, the challenges of navigating an unfamiliar environment-from language barriers to logistical mishaps-build resilience and self-reliance. We learn that we are capable of more than we thought and that the world is generally a more welcoming place than we were led to believe. However, this growth only occurs if we approach our journeys with an open heart and a willingness to be changed. Travel is not just an escape from our daily lives; it is a mirror that reveals who we are when all our familiar structures are stripped away.",
        ),
    ],
    "c1": [
        (
            "The Ephemeral Allure of the Uncharted",
            "There is a pervasive, almost romanticized notion that the modern traveler can still encounter truly uncharted territory. In an age of satellite imagery and ubiquitous digital mapping, the physical frontiers of our planet have largely been cataloged, yet the psychological frontier remains as vast as ever. The nuance of contemporary exploration lies not in the discovery of new landmasses, but in the subjective interpretation of space and time. For the discerning traveler, the allure of a destination often resides in its perceived authenticity-a quality that is increasingly elusive in a world governed by globalized aesthetics. We find ourselves in a paradoxical pursuit: seeking out hidden gems that, by the very act of our discovery and subsequent documentation, begin to lose the clandestine charm that made them desirable in the first place. This tension between preservation and consumption is the defining characteristic of elite tourism. To travel with sophistication today is to acknowledge one's own role in this delicate ecosystem and to seek a mode of engagement that prioritizes intellectual humility over the mere accumulation of experiences.",
        ),
        (
            "The Architecture of Memory: Why We Revisit Destinations",
            "The act of revisiting a beloved destination is rarely about seeing the sights; rather, it is a conscious engagement with the architecture of our own memories. When we return to a specific piazza in Rome or a fog-shrouded street in London, we are not merely tourists in a city, but pilgrims in our own past. The city becomes a palimpsest-a physical surface upon which our previous selves have left their mark. There is a profound comfort in the familiar, a sentimental geography that allows us to measure our personal growth against the static backdrop of historic monuments. However, this nostalgia is a double-edged sword. To return to a place is to confront the inevitable discrepancy between the idealized memory and the current reality. The shop that once defined a street corner has vanished; the light falls differently across the square. The sophisticated traveler understands that one can never truly go back. Instead, we return to synthesize these layers of experience, creating a richer, more nuanced understanding of both the destination and the trajectory of our own lives.",
        ),
        (
            "The Ethics of Aestheticizing Poverty",
            "The rise of slum tourism and the commodification of underprivileged neighborhoods have sparked a tumultuous ethical debate within the global travel community. Proponents argue that such tours foster social awareness and provide a vital source of income for marginalized communities. Critics, conversely, suggest that they often amount to little more than a voyeuristic aestheticization of poverty, where the struggles of local residents are transformed into a backdrop for the traveler's own narrative of self-discovery. The nuance of this debate lies in the power dynamic between the observer and the observed. For a tour to be ethically defensible, it must transcend the superficial and focus on genuine human agency and systemic context. It requires a shift from passive observation to active solidarity. Without a rigorous ethical framework, these interactions risk reinforcing paternalistic stereotypes and further alienating the very populations they claim to support. As travelers, we must interrogate our own motivations: are we seeking understanding, or are we merely consuming an edgy experience to enhance our own cultural capital?",
        ),
        (
            "The Linguistic Threshold: Beyond the Phrasebook",
            "While English has undeniably solidified its status as the global lingua franca, relying solely on its convenience can lead to a sterilized and detached travel experience. The linguistic threshold-the point at which a traveler moves beyond basic transactional phrases into meaningful dialogue-is where the true essence of a culture is revealed. Language is not merely a vehicle for information; it is a repository of cultural temperament, history, and social hierarchy. When you engage with a local in their mother tongue, you are acknowledging the sovereignty of their worldview. There are nuances of sentiment-the Portuguese saudade, the Japanese wabi-sabi-that simply do not translate without losing their emotional resonance. To study a language before traveling is to perform an act of intellectual respect. It allows the traveler to navigate the subtle social codes and idiomatic expressions that define daily life. In an increasingly homogenized world, the effort to bridge the linguistic divide is perhaps the most effective way to preserve the diversity of human experience.",
        ),
        (
            "The Paradox of the Authentic Experience",
            "In the lexicon of modern travel, authenticity is the ultimate, albeit most problematic, prize. We speak of authentic street food, authentic festivals, and authentic interactions, yet the very pursuit of this quality often renders it performative. Once a cultural practice is identified as authentic by the global tourism industry, it frequently adapts to meet the expectations of the foreign gaze. The nuance of authenticity is that it is not a static artifact but a living, evolving process. A traditional dance performed in a village square is no less authentic if the performers check their smartphones during a break. Authenticity resides in the mundane and the contemporary as much as it does in the historical. The sophisticated traveler must move beyond the search for an idealized, frozen-in-time version of culture and embrace the contradictions of the present. To find the real version of a place, one must be willing to engage with its complexities, its modernities, and even its disappointments, rather than demanding a curated spectacle that fits a preconceived narrative.",
        ),
        (
            "The Geopolitics of the Passport",
            "We often think of travel as a universal human right, yet the reality is that the ability to move across borders is one of the most significant indicators of geopolitical privilege. The strength of a passport-determined by the number of countries one can enter visa-free-reflects a complex web of historical alliances, economic standing, and diplomatic leverage. For those with high-ranking passports, borders are often mere administrative formalities; for those from the Global South, they can be insurmountable barriers. This disparity creates a stratified global mobility where the global citizen is, in fact, a very specific demographic profile. The nuance of this privilege is that it is often invisible to those who possess it. To travel with a powerful passport is to move through a world that has been engineered for your convenience. Acknowledging this inequality is essential for a more critical and empathetic understanding of global movement. Travel is not just about personal discovery; it is a direct engagement with the structures of power that dictate who is allowed to belong in which space.",
        ),
        (
            "The Slow Descent: The Psychology of Long-Haul Travel",
            "Long-haul travel is a profound exercise in temporal and spatial disorientation. As we hurtle across time zones at thirty thousand feet, our biological rhythms are severed from the environment below. This liminal space-the state of being neither here nor there-induces a unique psychological temperament. It is a period of forced introspection, a temporary suspension of daily responsibilities that can lead to unexpected clarity or existential anxiety. The nuance of this experience is the physical toll it exacts on the psyche; the jet lag is not just a physiological disruption but a cognitive one. We arrive in a new destination as ghosts of our former selves, our minds trailing behind our bodies across the ocean. The sophisticated traveler understands that the journey itself is a necessary part of the transition. It is a slow descent into a new reality, a period of incubation that allows the traveler to shed the habits of home and prepare for the sensory demands of the unknown.",
        ),
        (
            "The Commodification of Wilderness",
            "The growing demand for eco-tourism and luxury glamping represents a fascinating, if contradictory, development in our relationship with the natural world. We seek out the wilderness as a sanctuary from the digital noise of urban life, yet we increasingly demand that this wilderness be accessible, comfortable, and Instagrammable. This commodification of the wild creates a paradox: to protect a natural area, we often turn it into a managed park, complete with designated paths, visitor centers, and luxury lodges. The nuance here is the tension between conservation and consumption. While tourism revenue can fund vital ecological protection, the infrastructure required to host tourists can itself disrupt the very ecosystems we wish to admire. Furthermore, the wilderness we consume is often a carefully curated version of nature, stripped of its inherent dangers and inconveniences. True engagement with the wild requires a willingness to surrender our desire for control and to acknowledge our own smallness in the face of ecological forces that do not exist for our entertainment.",
        ),
        (
            "The Art of the Flaneur in the Digital Age",
            "The 19th-century concept of the flaneur-the urban explorer who wanders aimlessly through the city, observing the crowd without a specific destination-has found a new and complex resonance in the age of GPS. Today, our movements are increasingly dictated by algorithms that suggest the most efficient route or the top-rated attractions. The flaneur of the 21st century must perform an act of digital rebellion. To truly experience the city is to intentionally ignore the blue dot on the screen and allow oneself to be led by sensory curiosity. The nuance of modern urban exploration is the ability to find the gaps in the digital map-the places that have not yet been optimized for the tourist gaze. This intentional wandering is a way of reclaiming our autonomy and our sense of wonder. It is through the accidental discovery of a hidden courtyard or a local dive bar that we forge a personal connection with a city, transforming it from a series of coordinates into a lived experience that is uniquely our own.",
        ),
        (
            "The Colonial Echo in Modern Tourism",
            "It is an uncomfortable but necessary truth that much of modern international tourism is built upon the structural legacies of colonialism. The routes we travel, the languages we speak, and even the exotic appeal of certain destinations are often rooted in historical power imbalances. The white gaze frequently dictates how non-Western cultures are marketed and consumed, often emphasizing a sense of otherness that reinforces old hierarchies. The nuance of this critique is not to suggest that all travel is inherently colonial, but to encourage a more rigorous self-reflection. How do our spending habits, our interactions with local staff, and our expectations of service reflect these deep-seated biases? To travel ethically in the 21st century is to engage in a process of decolonizing our own perspectives. It requires a commitment to reciprocity, an effort to support local ownership, and a willingness to listen to the narratives of a place as told by its own people, rather than through the lens of a Western guidebook.",
        ),
    ],
    "c2": [
        (
            "The Cartography of Absence: On the Metaphysics of Lost Places",
            "The contemporary obsession with total documentation-the relentless mapping of every square meter of our planet's surface-has inadvertently birthed a new kind of existential anxiety: the death of the elsewhere. When satellite imagery and street-level digital renderings allow us to inhabit a space before we even arrive, the act of travel risk becoming a redundant verification of a pre-consumed reality. The nuance of the C2 traveler's journey lies in the pursuit of what might be termed the cartography of absence. This is not a search for new lands, but a deliberate engagement with the gaps in the digital narrative, the places that have slipped through the cracks of the algorithm. In these liminal spaces, we find the terra incognita of the spirit. True exploration today is an exercise in intellectual resistance; it is the refusal to let the blue dot on a screen dictate the boundaries of our curiosity. We must learn to navigate by the stars of our own intuition, reclaiming the silence and the uncertainty that once defined the human experience of the world. To travel in this sense is to seek a confrontation with the unquantifiable, to acknowledge that the most profound journeys are those that cannot be tracked, saved, or shared.",
        ),
        (
            "The Palimpsest of the Polis: Chronotopic Disorientation in Historic Cities",
            "To walk through the streets of an ancient city is to engage in a form of temporal vertigo. The urban fabric is a palimpsest, a dense layering of epochs where the medieval alleyway abruptly intersects with the glass-and-steel hubris of late capitalism. For the sophisticated observer, this chronotopic disorientation is not a source of confusion, but a profound aesthetic pleasure. We are not merely moving through space; we are moving through a vertical accumulation of human intent. The nuance of this experience is the ability to read the city's scars-the repurposed stones of a Roman theater in a Renaissance palace, the ghostly outlines of vanished walls in the curvature of a modern street. This is the deep time of the polis, a reality that defies the linear narrative of the guidebook. To truly inhabit such a city is to acknowledge that we are ephemeral guests in a dialogue that has lasted millennia. The journey becomes a meditation on the permanence of the collective and the transience of the individual, a realization that the city is not a static museum, but a living, breathing entity that absorbs our presence into its ever-thickening layers of history.",
        ),
        (
            "The Seduction of the Liminal: The Psychology of the Non-Place",
            "Anthropologist Marc Auge coined the term non-place to describe the transient spaces of late modernity-airports, motorway service stations, hotel chains-spaces that are characterized by their lack of historical identity or organic social relations. While many travelers revile these environments for their sterile homogeneity, there is a subtle, almost seductive allure in their very anonymity. In the non-place, one is liberated from the burden of social identity; you are a ghost in a machine designed for pure transit. This liminality induces a state of heightened self-awareness, a cognitive suspension where the normal rules of engagement are replaced by a profound, solitary introspection. The nuance of the C2 experience in these spaces is the recognition of their aesthetic of the ephemeral. The airport lounge at 3 AM becomes a secular sanctuary, a place where the globalized world pauses for breath. To find beauty in the non-place is to acknowledge that our modern condition is one of perpetual displacement. It is in these sterile corridors that we often find the most honest reflection of our fragmented, hypermobile lives, stripped of the cultural ornaments that usually define our sense of belonging.",
        ),
        (
            "The Geopolitical Soul of the Border: A Meditation on Liminality",
            "The border is frequently reduced to a mere administrative line, a legal threshold between sovereignties. However, for the philosophically inclined traveler, the border is a profound metaphysical site-a place where the fiction of the nation-state is most visible and most fragile. To stand at a border is to exist in a state of geopolitical suspense, where the here and the there are defined by the arbitrary stroke of a pen on a map. The nuance of this experience is the palpable tension between the rigidity of the law and the fluidity of the landscape. Nature, of course, ignores the border; the river flows and the mountain stands, indifferent to the passports and the wire. The sophisticated traveler observes the borderland culture-that unique, hybridized identity that emerges in the shadow of the checkpoint, where languages bleed into one another and the binary of us and them begins to unravel. The border is a mirror that reflects the anxieties of the center; to understand a nation, one must observe it from its edge, where its definitions are most contested and its vulnerability most exposed.",
        ),
        (
            "The Aesthetic of the Ruin: On the Poetics of Decay",
            "There is a profound, albeit melancholy, pleasure in the observation of architectural decay. The ruin is a site where nature reasserts its sovereignty over the hubris of human construction, a visual representation of the inexorable passage of time. For the traveler who seeks the nuance of the C2 experience, the ruin is not a symbol of failure, but a testament to the cycles of civilization. In the crumbling columns of a temple or the rusting infrastructure of a vanished industry, we find the sublime of the obsolete. This is a poetics of the fragment, where the absence of the whole allows the imagination to construct its own narratives of the past. The danger of modern tourism is the sanitization of the ruin-the turning of a site of tragic beauty into a safe, ticketed attraction. True engagement with decay requires a willingness to confront our own mortality and the inevitable obsolescence of our own era. The ruin is a memento mori on a civilizational scale, a reminder that the world we build is merely a temporary interruption in the silence of the landscape.",
        ),
        (
            "The Paradox of the Digital Nomad: Rootlessness in a Connected World",
            "The digital nomad is often celebrated as the ultimate expression of modern freedom-a sovereign individual untethered by geography, earning a living in the ether while wandering the globe. However, this lifestyle conceals a profound ontological paradox: the more we are connected to the digital everywhere, the more we risk being rooted in nowhere. The nuance of this condition is the erosion of the sense of place. When one's environment is merely a backdrop for a laptop screen, the physical reality of a destination becomes a commodity, a vibe to be consumed rather than a community to be engaged with. This rootlessness can lead to a kind of cultural anorexia-a diet of superficial experiences that never satisfy the human need for deep, generational belonging. The C2 nomad is one who recognizes this trap and actively resists it, seeking out the friction of local life that cannot be digitized. It is the realization that true freedom is not the absence of ties, but the ability to choose where we plant our roots, even if only temporarily, and to acknowledge the weight of our footprint in the places we inhabit.",
        ),
        (
            "The Linguistic Exile: On the Solitude of the Foreign Tongue",
            "To live in a country where one does not speak the language fluently is to experience a unique and profound form of exile. It is the exile of the interior self, where the complexity of one's thoughts is trapped behind the simplicity of one's vocabulary. For the sophisticated traveler, this linguistic isolation is not merely a frustration, but a vital philosophical exercise. It forces a return to the pre-linguistic, to a reliance on gesture, tone, and the subtle semiotics of the body. There is a strange, quiet dignity in this forced simplicity; it strips away the ego that is built upon verbal prowess. The nuance of this state is the solitude of the foreign tongue, a condition that heightens the powers of observation. When you cannot speak, you must listen with a different kind of intensity. You begin to hear the music of the language rather than its meaning, and you perceive the social dynamics of a space through the rhythm of its interactions. This linguistic humility is the ultimate antidote to the hubris of the global traveler; it is a reminder that we are all, at our core, foreigners seeking to be understood in a world that is fundamentally indifferent to our explanations.",
        ),
        (
            "The Ethics of the Gaze: On the Voyeurism of the Exotic",
            "The exotic is a category that exists only in the eye of the beholder; it is a projection of otherness onto a culture that is perfectly mundane to those who inhabit it. The sophisticated traveler must grapple with the ethics of this gaze, acknowledging that the very act of observing a traditional culture can transform it into a spectacle. The nuance here is the subtle power dynamic inherent in the tourist-local relationship-a relationship that is often built upon a foundation of economic inequality. When we seek out authentic experiences in the Global South, are we engaging in a meaningful cross-cultural dialogue, or are we merely performing a sophisticated form of voyeurism? To travel with a C2 level of ethical awareness is to recognize our own role in the commodification of culture. It requires a move toward reciprocity, a commitment to supporting the agency of the local population rather than demanding that they perform an idealized version of themselves for our entertainment. The ultimate goal of travel should be the dismantling of the exotic, the realization that there is no other, only different ways of being human in a shared and fragile world.",
        ),
        (
            "The Sublime of the Void: Traveling Through the Desert",
            "The desert has historically been a site of spiritual revelation and existential testing-a landscape defined not by what is there, but by what is absent. To travel through the desert is to experience the sublime of the void, a confrontation with a scale of time and space that renders human concerns trivial. The nuance of the C2 experience in the wilderness is the psychological impact of the silence. In our hyperconnected lives, we are rarely truly alone with our own thoughts; the desert provides the ultimate acoustic and visual isolation. This is not a scenic trip; it is a descent into the essential. The desert strips away the ornaments of civilization, leaving only the fundamental elements of light, wind, and stone. For the traveler who can endure it, this void is not empty, but full of a terrifying and beautiful clarity. It is a reminder that the world does not exist for our comfort, and that our mastery over nature is a fragile illusion that can be wiped away by a single sandstorm. To love the desert is to love the world in its most uncompromising and honest form.",
        ),
        (
            "The Return as an Act of Translation: On the Impossibility of Sharing",
            "The final, and perhaps most difficult, stage of any journey is the return. The sophisticated traveler knows that the person who comes back is not the same person who left, yet the world they return to is unchanged. This creates a profound disconnection of the returned-the realization that the most transformative experiences of the trip are precisely the ones that cannot be communicated. To share a journey is an act of translation, and like all translations, it is an exercise in loss. The nuance of the C2 return is the acceptance of this silence. We speak of the food, the weather, and the sights, but we remain silent about the subtle shift in our internal landscape, the moment of grace in a foreign cathedral, or the crushing loneliness of a crowded city. These are the untranslatable memories that form the true substance of the journey. The return is not the end of the trip, but the beginning of the long process of integrating these new, silent layers of the self into the familiar structures of home.",
        ),
    ],
}


LEVEL_NOTES = {
    "iniciante": "presente simples, estruturas de repeticao e vocabulario concreto",
    "a1": "rotina de viagem, verbos basicos e conectores simples",
    "a2": "narrativas curtas, passado simples e comparativos",
    "b1": "opinioes, causa e consequencia, conectores variados",
    "b2": "argumentacao, ideias abstratas e vocabulario avancado",
    "c1": "nuance, estilo, opinioes complexas e estruturas variadas",
    "c2": "texto refinado, inferencia, ambiguidade e registros eruditos",
}


class Command(BaseCommand):
    help = "Replace the Viagens catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="viagens")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = TRAVEL_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-viagens-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Viagens texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre viagens: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D cartoon style, clean lines, high quality, "
            f"educational travel scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
