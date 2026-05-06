import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from reading.artwork import write_text_illustration
from reading.content_pipeline import LEVEL_WORD_LIMITS, replace_text_vocabulary
from reading.models import Category, Level, Text


READABLE_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[A-Za-z0-9'-]*[A-Za-z0-9])?")


ENVIRONMENT_TEXTS = {}


ENVIRONMENT_TEXTS["iniciante"] = [
    (
        "The Big Green Tree",
        "There is a big green tree in the garden. The tree is very tall. It has many green leaves. In the summer, the tree gives cold shade. Birds live in the branches of the tree. The tree is good for the air. I like to sit under the tree and read. Trees are beautiful and important for our world.",
    ),
    (
        "The Blue Ocean",
        "The ocean is very big and blue. The water is salt and cold. Many fish live in the ocean. Some fish are small and some are very big. I see the blue water and the white sand. The ocean is beautiful. We need to keep the water clean for the fish. The ocean is a magic place.",
    ),
    (
        "The Yellow Sun",
        "The sun is in the sky. It is big and yellow. The sun is very hot. It gives light to the plants. It gives warmth to the animals. In the morning, the sun is bright. In the evening, the sun is orange. We need the sun to live. The sun is a powerful star in our world.",
    ),
    (
        "Clean Water",
        "Water is very important for life. People drink water. Animals drink water. Plants need water to grow. There is water in the rivers and in the rain. We must keep the water clean. Dirty water is bad for the world. I drink a glass of water every day. Clean water is a treasure.",
    ),
    (
        "Flowers in the Park",
        "There are many flowers in the park. Some flowers are red and some are purple. The flowers smell very sweet. Bees like the flowers. I see the flowers in the spring. The park is a green and happy place. We do not pick the flowers. We look at them and smile. Nature is colorful.",
    ),
    (
        "The Little Bee",
        "A bee is a small insect. It is yellow and black. The bee flies from flower to flower. It makes honey. Honey is very sweet. Bees are very important for the plants. I see a bee in the garden. I do not touch the bee. It is busy with its work. Small animals are important, too.",
    ),
    (
        "Recycling Paper",
        "This is a blue bin. I put paper in the blue bin. This is called recycling. Recycling is good for the trees. We use old paper to make new paper. It is a simple habit. I recycle paper at home and at the university. My family helps the world. Recycling is a great way to protect nature.",
    ),
    (
        "The High Mountains",
        "The mountains are very high and gray. Some mountains have white snow on top. The air in the mountains is very cold and fresh. I see the mountains from far away. They are strong and old. Many animals live in the rocks. I like to look at the high mountains. The earth is very big.",
    ),
    (
        "A Green Garden",
        "I have a small garden at home. There is green grass and small plants. I put water on the plants every morning. The plants are happy in the sun. I see a small butterfly in the grass. The butterfly is orange and black. My garden is a quiet place. I love my green garden and the nature.",
    ),
    (
        "Picking Up Trash",
        "I see trash on the ground. This is not good for the earth. I pick up the plastic bottle. I put the trash in the bin. Now the park is clean. Keeping the world clean is our job. It is easy to help nature. A clean place is a healthy place for everyone. I love my planet.",
    ),
]


ENVIRONMENT_TEXTS["a1"] = [
    (
        "The Three Rs: Reduce, Reuse, Recycle",
        "Taking care of the planet is very simple if we follow the three Rs. First, we need to reduce our waste because we buy many things we do not need. Second, we should reuse plastic bottles and glass jars instead of throwing them away. Finally, we must recycle paper, metal, and plastic in the correct bins. My family is going to start a recycling project at home this weekend. These small actions are important because they help save the trees and keep the oceans clean. Everyone can help the environment every day with these easy habits.",
    ),
    (
        "Global Warming and Our Weather",
        "The earth is getting warmer every year, and scientists call this global warming. This happens because there is too much pollution in the air from cars and factories. Because of the heat, the ice in the Arctic is melting and the sea level is rising. This is dangerous for animals like polar bears and for people living near the coast. We are going to use more clean energy, like sun and wind power, to help the planet. If we plant more trees and drive less, we can stop the temperature from rising too fast. Protecting our atmosphere is very important.",
    ),
    (
        "Saving the Rainforest",
        "Rainforests are often called the lungs of the planet because they produce a lot of oxygen. Many exotic animals and beautiful plants live in these green forests. However, people are cutting down many trees to build farms and roads. This is a big problem because the animals lose their homes and the air becomes dirty. I am going to study more about the Amazon rainforest for my university project. We need to protect these forests because they help regulate the world's climate. Saving the trees means saving the life on our beautiful Earth.",
    ),
    (
        "The Problem with Plastic in the Ocean",
        "There is a lot of plastic trash in the ocean today, and it is hurting the sea animals. Turtles and fish sometimes eat plastic because they think it is food. This is very sad and dangerous for the marine life. To help, I am going to stop using plastic straws and bags. I use a reusable water bottle every day when I go to the university. We also need to participate in beach clean-ups to remove the trash from the sand. If we use less plastic, the ocean is going to be a safer place for all creatures.",
    ),
    (
        "Why Bees are Important for Nature",
        "Bees are small insects, but they have a very big job in nature. They fly to different flowers and help them grow fruits and vegetables. This process is called pollination. Without bees, we are not going to have many of the foods we eat every day, like apples and coffee. Unfortunately, many bees are dying because of chemicals on farms. To help them, my neighbor is going to plant a garden with many colorful flowers. We must protect the bees because they are essential for the environment and for our food.",
    ),
    (
        "Saving Energy at Home",
        "Saving energy is a great way to help the environment and save money. When I leave a room, I always turn off the lights. I am also going to use LED bulbs because they use less electricity. We should not leave the television or the computer on during the night. In the winter, I wear a warm sweater instead of using a lot of heating. These actions are good because factories produce less pollution when we use less energy. If everyone saves a little bit of energy, it makes a huge difference for our planet.",
    ),
    (
        "Water Conservation Habits",
        "Clean water is a limited resource, so we must use it carefully. I am going to take shorter showers to save many liters of water every week. When I brush my teeth, I always close the tap. Some people use rainwater to water their plants in the garden, and this is a fantastic idea. We should never throw chemicals or trash into the rivers because it kills the fish. Because every drop is important, we need to be responsible with our water. A world with clean water is a healthy world for everyone.",
    ),
    (
        "Planting a Tree for the Future",
        "Next Saturday, my classmates and I are going to plant ten trees in the local park. Planting a tree is a gift for the future because trees provide shade and fresh air. They also give food and protection to birds and small animals. Trees help to cool the city during the hot summer days in Brasilia. I think that every student should plant at least one tree during their life. It is a beautiful way to connect with nature and help the Earth. Our small forest is going to grow big and strong over the years.",
    ),
    (
        "The Importance of Endangered Animals",
        "Some animals are in danger of disappearing forever, like the giant panda and the blue whale. These are called endangered species. They are disappearing because people hunt them or destroy their natural habitats. We need to support organizations that protect these animals and their homes. I am going to read a book about wildlife conservation to learn how to help. Biodiversity is important because every animal has a role in nature. We must act now to ensure that these beautiful creatures stay on our planet for a long time.",
    ),
    (
        "Walking and Biking to School",
        "Cars produce a lot of CO2, which is bad for the air we breathe. To help the environment, I am going to walk or ride my bike to the university more often. It is a healthy habit for me and for the planet. Walking is free and it reduces the traffic in the city. When I need to go far, I prefer to use the bus or the subway because public transport is better for the environment than many private cars. If we change how we travel, our cities are going to have cleaner air and less noise.",
    ),
]


ENVIRONMENT_TEXTS["a2"] = [
    (
        "A Clean-up Day at the Lake",
        "Last month, my classmates and I organized a clean-up day at Paranoa Lake in Brasilia. When we arrived, the shore was much dirtier than we expected. We found more plastic bottles and old tires than last year. We worked for five hours and collected thirty large bags of trash. After our work, the area looked significantly more beautiful and organized. We also noticed that the water seemed clearer than before. It was a tiring day, but we felt much happier because we helped the local ecosystem. This experience proved that a small group of students can make a place cleaner and safer for the birds and fish. We decided that this year's project was more successful than our previous one because more volunteers joined us.",
    ),
    (
        "Switching to Solar Energy",
        "Two years ago, my family decided to install solar panels on the roof of our house. Before that, our electricity bill was much more expensive, and we used energy from less sustainable sources. The installation process was faster than I imagined, and the technicians were very professional. Now, our home produces its own clean energy from the sun. In my opinion, solar power is better than traditional energy because it does not produce pollution. Last summer was hotter than usual, but our system worked perfectly. Although the initial cost was high, we are saving more money now than in the past. We are very proud because our carbon footprint is smaller today, and we are helping the planet every day.",
    ),
    (
        "The Forest Before and After",
        "I visited a national park near my city last weekend. My grandfather told me that thirty years ago, the forest was much larger and denser than it is today. He said there were more wild animals and the air felt fresher in the past. Unfortunately, because of new roads and farms, the park is smaller now. I saw many areas where people cut down trees, and it was sadder than I thought. However, I also saw a new section where volunteers planted thousands of young trees recently. These new trees are still smaller than the old ones, but they are growing fast. I believe that if we protect the park now, it can become as beautiful as it was in my grandfather's stories.",
    ),
    (
        "My First Organic Garden",
        "Last spring, I started my first organic garden in my backyard. In the beginning, it was more difficult than I expected because I didn't want to use chemical pesticides. I used natural compost instead, which was stickier and smellier than store-bought fertilizers, but much better for the soil. I planted tomatoes, carrots, and lettuce. After two months, my vegetables were larger and tastier than the ones I buy at the supermarket. My friends said that my organic lettuce was the freshest they ever ate! Although I spent more time pulling weeds than I planned, the result was very rewarding. I realized that growing your own food is a healthier and more sustainable way to live.",
    ),
    (
        "Comparing City Life and Countryside Air",
        "Last vacation, I traveled from the busy city center to a small village in the mountains. The difference in air quality was immediate. In the city, the air is often grayer and more polluted because of the heavy traffic. In the mountains, the air felt much thinner and cleaner than in Brasilia. I could breathe more easily, and the sky was bluer during the day. At night, I saw more stars because there was less light pollution than in the city. Although the city is more convenient for work and study, the countryside is much better for your lungs and your mental health. This trip showed me that we must work harder to reduce pollution in our urban areas.",
    ),
    (
        "From Plastic to Bamboo",
        "Last year, I decided to replace most of my plastic items with more sustainable alternatives. I bought a bamboo toothbrush, which felt a bit rougher at first, but now I like it more than my old plastic one. I also started using a metal straw because it is more durable and easier to clean. My new reusable shopping bags are stronger than the thin plastic bags from the supermarket, and they can carry more weight. Making these changes was simpler than I thought, and I feel better because I am producing less waste. I realized that sustainable products are often better quality than cheap plastic things. I hope more people choose these alternatives to protect our oceans.",
    ),
    (
        "A Lesson About Endangered Species",
        "In my biology class last week, we watched a documentary about the blue whale. I learned that these animals are much larger than any dinosaur that ever lived! In the past, there were thousands of blue whales in the ocean, but people hunted them, and their population became much smaller. Today, they are more protected than before, but they still face many dangers from plastic and climate change. The documentary showed that the ocean is more silent and empty without these giants. I felt more motivated to support wildlife conservation after learning about their history. Protecting endangered species is more important today than it was in the past because we are losing biodiversity very fast.",
    ),
    (
        "The Great Drought of 2024",
        "I remember the great drought that happened two years ago. The weather was much drier and hotter than usual, and it didn't rain for many months. The rivers became lower than I ever saw them before. Because of the lack of water, the government asked everyone to use less water at home. We took shorter showers and stopped washing our cars. The grass in the parks became yellower and drier than in the winter. It was a very difficult time for the farmers because their crops were smaller and weaker. This event taught me that water is more precious than we think. Now, I am much more careful with every drop of water I use.",
    ),
    (
        "Learning to Compost at the University",
        "Last semester, my university started a new composting program in the cafeteria. Before this program, all the food waste went to the trash cans, which was very bad for the environment. Now, we put fruit peels and leftover vegetables in special green bins. This organic waste is turned into fertilizer for the university gardens. I noticed that the gardens are now greener and the flowers are more colorful than last year. The composting process is more interesting than I imagined, and it is a great way to reduce the amount of trash that goes to the landfill. I think this program is better than just recycling because it creates something useful for nature.",
    ),
    (
        "Biking is Better Than Driving",
        "Last month, I stopped using my car to go to the internship and started riding my bike. In the beginning, I was slower than the cars, and the hills were more difficult than I expected. However, after two weeks, I became faster and stronger. Biking is much cheaper than driving because I don't need to pay for gas or parking. Also, my bike is more eco-friendly than a car because it doesn't produce any CO2. I feel more energetic in the morning now than when I sat in traffic for an hour. Although rainy days are more challenging, I still prefer my bike. It is a better choice for my health and for the atmosphere of my city.",
    ),
]


ENVIRONMENT_TEXTS["b1"] = [
    (
        "The True Cost of Fast Fashion",
        "The fashion industry is currently one of the largest polluters in the world, primarily due to a trend known as fast fashion. This business model relies on producing massive amounts of cheap clothing to satisfy rapidly changing trends. Consequently, millions of tons of garments end up in landfills every year because the quality is too poor for long-term use. Furthermore, the production process consumes enormous quantities of water and involves toxic dyes that often contaminate rivers in developing nations. In my opinion, as consumers, we must shift our focus toward slow fashion by choosing durable, high-quality pieces. Although these items are more expensive, they last much longer and have a significantly lower environmental impact. Therefore, we should prioritize ethical brands and consider buying second-hand clothes to reduce our individual footprint. In conclusion, our shopping habits have a direct effect on the health of the planet, so we must choose quality over quantity.",
    ),
    (
        "The Vital Importance of Urban Green Spaces",
        "As cities continue to grow, the preservation of urban green spaces, such as parks and botanical gardens, has become essential for public health and environmental stability. These areas are vital because trees and plants act as natural filters, removing carbon dioxide and pollutants from the air. Consequently, cities with more vegetation tend to have better air quality and lower temperatures during the summer. Furthermore, green spaces provide a necessary habitat for local wildlife, such as birds and insects, which helps maintain urban biodiversity. In my view, local governments should prioritize the creation of more parks, especially in densely populated neighborhoods. Not only do these spaces benefit the environment, but they also improve the mental well-being of residents by providing a place to relax and connect with nature. Therefore, protecting the green lungs of our cities is not a luxury, but a fundamental requirement for a sustainable urban future.",
    ),
    (
        "Renewable Energy: A Necessity for the Future",
        "The transition from fossil fuels to renewable energy sources, such as solar, wind, and hydroelectric power, is no longer an option but a necessity. Burning coal and oil produces greenhouse gases, which are the primary cause of global warming and extreme weather events. Consequently, if we do not change our energy infrastructure, the planet will continue to face rising sea levels and severe droughts. Furthermore, renewable energy is becoming increasingly affordable and can create thousands of new jobs in the technology sector. In my opinion, governments should provide more incentives for families and businesses to install solar panels and wind turbines. Although the initial investment can be high, the long-term benefits for the atmosphere and the economy are undeniable. Therefore, we must accelerate the move toward a carbon-neutral society to ensure a safe environment for future generations.",
    ),
    (
        "The Hidden Impact of Food Waste",
        "Food waste is a significant environmental issue that many people overlook. When we throw away food, we are also wasting all the resources-such as water, energy, and labor-that were used to produce, transport, and package it. Furthermore, when food rots in landfills, it produces methane, a greenhouse gas that is much more potent than carbon dioxide. Consequently, reducing food waste is one of the most effective ways to fight climate change. In my view, we should be more organized when we go grocery shopping by creating lists and planning our meals in advance. We can also help by composting organic scraps at home instead of throwing them in the regular trash. Therefore, being mindful of what we eat and what we discard is a powerful way to protect the Earth's limited resources.",
    ),
    (
        "Why We Must Protect Our Oceans",
        "The oceans cover more than 70% of the Earth's surface and are responsible for producing half of the world's oxygen. However, they are currently facing multiple threats, including plastic pollution, overfishing, and acidification. Because the ocean absorbs a lot of heat and CO2, it plays a crucial role in regulating the global climate. Consequently, if the marine ecosystem collapses, the consequences for human life will be catastrophic. Furthermore, millions of people depend on the ocean for their food and livelihoods. In my opinion, we need stricter international laws to prevent companies from dumping industrial waste into the sea. We should also support marine protected areas where fishing is prohibited to allow populations to recover. Therefore, protecting our oceans is not just about saving charismatic animals; it is about protecting the life-support system of our entire planet.",
    ),
    (
        "The Concept of the Circular Economy",
        "The traditional linear economy follows a pattern of take, make, and dispose, which is incredibly wasteful and damaging to the environment. In contrast, the circular economy aims to eliminate waste by keeping products and materials in use for as long as possible. This involves designing items that are easy to repair, refurbish, and recycle. Consequently, we can significantly reduce the amount of raw materials we extract from the Earth. Furthermore, this model encourages businesses to offer services instead of just products, such as leasing appliances instead of selling them. In my view, the circular economy is the only sustainable path for a planet with finite resources. Although it requires a major shift in how we think about production and consumption, it offers a way to maintain our quality of life without destroying the environment. Therefore, we should support companies that embrace circularity and demand more durable products.",
    ),
    (
        "How Technology Can Help Save the Environment",
        "Technology is often blamed for environmental degradation, but it can also be a powerful tool for conservation. For instance, satellite imaging and drones allow scientists to monitor deforestation and illegal poaching in remote areas in real-time. Furthermore, advancements in data engineering and AI are helping cities optimize their energy use and improve waste management systems. Consequently, we are becoming more efficient at using resources and reducing our impact on nature. In my view, innovation in green technology-such as biodegradable plastics and carbon capture systems-is essential for solving the climate crisis. However, technology alone is not enough; we also need political will and changes in human behavior. Therefore, we should invest in scientific research while also promoting a culture of sustainability and respect for the natural world.",
    ),
    (
        "The Importance of Biodiversity in Agriculture",
        "Modern industrial agriculture often relies on monocultures, where only one type of crop is grown over a large area. While this is efficient for production, it is very dangerous for the environment because it reduces biodiversity and makes the soil weaker. Consequently, farmers have to use more chemical fertilizers and pesticides to protect their crops. Furthermore, if a specific disease attacks that crop, the entire food supply is at risk. In my opinion, we should encourage polycultures and organic farming methods that work in harmony with nature. By planting a variety of crops, we can naturally improve soil health and provide habitats for beneficial insects like bees and butterflies. Therefore, supporting local farmers who use sustainable practices is a great way to ensure a resilient and healthy food system for everyone.",
    ),
    (
        "The Problem with Noise Pollution",
        "When we talk about the environment, we usually think about air or water, but noise pollution is also a serious threat to both humans and wildlife. In urban areas, constant noise from traffic, construction, and airplanes can lead to high stress levels and sleep disorders in people. Furthermore, for animals that rely on sound to communicate or hunt, such as birds and whales, excessive noise can be life-threatening. Consequently, it can disrupt migration patterns and reproduction cycles. In my view, we should design our cities with better acoustic insulation and more quiet zones like parks and pedestrian streets. We should also transition to electric vehicles, which are significantly quieter than internal combustion engines. Therefore, reducing noise is an essential part of making our world a healthier and more peaceful place for all living beings.",
    ),
    (
        "Individual Action vs. Systemic Change",
        "There is a constant debate about whether individual actions-like recycling or eating less meat-are enough to save the environment, or if we need massive systemic change from governments and corporations. In my opinion, both are equally important and interconnected. Individual actions are vital because they create a cultural shift and put pressure on businesses to change their products. Furthermore, when thousands of people make small changes, the cumulative effect is significant. However, without large-scale policies like carbon taxes and bans on single-use plastics, we cannot achieve the necessary goals in time. Therefore, we should continue to improve our personal habits while also advocating for stronger environmental laws. In conclusion, saving the planet requires a bottom-up and a top-down approach working together simultaneously.",
    ),
]


ENVIRONMENT_TEXTS["b2"] = [
    (
        "The Geopolitics of the Energy Transition",
        "The transition from fossil fuels to renewable energy is not merely a technical challenge; it is a profound geopolitical shift that is redefining global power structures. For decades, global politics was dictated by the control of oil and gas reserves. However, as nations move toward solar and wind power, the demand for critical minerals such as lithium, cobalt, and rare earth elements has surged. Consequently, countries that possess these resources or lead in the manufacturing of green technologies are gaining significant diplomatic leverage. Furthermore, if traditional oil-exporting nations fail to diversify their economies rapidly, they may face severe economic instability. In my opinion, international cooperation is essential to ensure that the green race does not lead to new forms of colonialism or conflict over mineral rights. We must ensure that the energy transition is both ecologically sound and socially just for the global south.",
    ),
    (
        "Carbon Capture and Storage: A Necessary Compromise?",
        "Carbon Capture and Storage (CCS) technology has emerged as a controversial yet potentially vital tool in the fight against climate change. The process involves capturing carbon dioxide emissions at their source, such as factories, and injecting them deep underground for permanent storage. Proponents argue that without CCS, it would be impossible to reach Net Zero targets, especially for industries like cement and steel production that are difficult to electrify. However, environmentalists worry that relying on this technology might encourage companies to continue burning fossil fuels instead of switching to renewables. Furthermore, there are concerns regarding the long-term safety of underground storage sites. In my view, CCS should be treated as a secondary solution rather than a primary strategy. If we had invested more in solar and wind decades ago, we might not have needed such expensive and complex engineering today.",
    ),
    (
        "The Ethics of De-extinction: Resurrecting Lost Species",
        "Advances in genetic engineering, particularly CRISPR technology, have brought the concept of de-extinction from science fiction to the verge of reality. Scientists are currently working on projects to resurrect species like the woolly mammoth and the passenger pigeon. The primary argument for de-extinction is that it could restore lost ecological functions and correct past human mistakes. Consequently, reintroducing these animals might help stabilize fragile ecosystems, such as the Arctic tundra. However, critics raise significant ethical questions: where would these animals live if their original habitats no longer exist? Furthermore, focusing on de-extinction might distract from the urgent need to protect currently endangered species. In my opinion, while the science is fascinating, we should prioritize the conservation of living biodiversity. It would be a tragedy if we spent millions bringing back the mammoth while allowing the elephant to go extinct.",
    ),
    (
        "The Economics of Natural Capital",
        "Traditional economic models often treat the environment as an externality, meaning that the depletion of natural resources is not factored into a country's Gross Domestic Product (GDP). To correct this, economists have developed the concept of Natural Capital, which assigns a financial value to ecosystem services like pollination, water purification, and carbon sequestration. Consequently, when a forest is preserved, its economic value as a carbon sink is recognized alongside its value as timber. Furthermore, this approach allows businesses to better understand the environmental risks in their supply chains. In my view, if we do not put a price on nature, it will continue to be exploited for short-term gain. However, we must be careful not to turn nature into just another commodity. The goal of natural capital accounting should be to protect life-support systems, not just to facilitate green-washing by large corporations.",
    ),
    (
        "Urban Resilience and the Sponge City Concept",
        "As climate change leads to more frequent and severe flooding, urban planners are adopting resilience strategies to protect metropolitan areas. One of the most innovative approaches is the Sponge City concept, which originated in China. Instead of relying on traditional concrete pipes and dams, a sponge city uses permeable pavements, rain gardens, and urban wetlands to absorb and filter rainwater. Consequently, this reduces the risk of floods while also recharging groundwater levels and cooling the city. Furthermore, these green infrastructures provide aesthetic and recreational benefits for residents. In my opinion, Brasilia and other major Brazilian cities could benefit significantly from such nature-based solutions, especially during the intense rainy seasons. If we had designed our cities to work with nature rather than against it, many modern urban disasters could have been avoided.",
    ),
    (
        "The Impact of Microplastics on Human Physiology",
        "While the visual impact of plastic pollution in the ocean is well-documented, the invisible threat of microplastics-particles smaller than five millimeters-is a growing concern for human health. These particles have been found in everything from bottled water to the seafood we consume. Recent studies indicate that microplastics can enter the human bloodstream and even cross the blood-brain barrier. Consequently, there is significant research being conducted on the potential long-term effects, such as chronic inflammation and endocrine disruption. Furthermore, microplastics often act as carriers for other toxic chemicals found in the environment. In my view, the only way to address this crisis is to implement a global ban on non-essential single-use plastics. We are currently participating in a massive, unintended biological experiment, and the results could be devastating for future generations.",
    ),
    (
        "Regulating the Greenwashing Phenomenon",
        "As consumers become more environmentally conscious, many companies have turned to greenwashing-the practice of making misleading or unsubstantiated claims about the environmental benefits of a product. For instance, a company might use green packaging or vague terms like eco-friendly without providing any specific data to support the claim. Consequently, this creates confusion in the market and makes it difficult for truly sustainable businesses to compete. To combat this, several countries are introducing stricter regulations and mandatory environmental labeling. Furthermore, independent auditors are being used to verify the carbon neutral claims of large corporations. In my opinion, greenwashing is a form of fraud that undermines the global effort to fight climate change. If we do not hold companies accountable for their environmental rhetoric, the transition to a sustainable economy will be fatally delayed.",
    ),
    (
        "Precision Agriculture and the Data-Driven Farm",
        "Precision agriculture is revolutionizing the way we produce food by using data engineering and satellite technology to optimize resource use. Farmers can now use GPS-guided tractors and sensors to apply the exact amount of water, fertilizer, and pesticides needed for each specific square meter of a field. Consequently, this significantly reduces waste and minimizes the chemical runoff that contaminates local water sources. Furthermore, AI models can predict weather patterns and pest outbreaks with high accuracy, allowing for proactive intervention. In my view, precision agriculture is essential for feeding a growing global population without destroying the environment. However, the high cost of this technology means that small-scale farmers in developing nations might be left behind. We must ensure that the digital revolution in farming is accessible to everyone, not just large-scale industrial producers.",
    ),
    (
        "The Tragedy of the Commons in the High Seas",
        "The High Seas-the vast areas of the ocean that lie outside national jurisdictions-represent a classic example of the Tragedy of the Commons. Because these waters belong to no one, they are often exploited by illegal fishing fleets and deep-sea mining companies. Consequently, fish populations are collapsing, and fragile deep-sea ecosystems are being destroyed before they can even be studied. Furthermore, the lack of legal oversight makes it difficult to enforce environmental standards or protect marine biodiversity. In my opinion, the recent High Seas Treaty is a landmark achievement, but its success will depend entirely on international enforcement. If we continue to treat the ocean as an infinite resource for extraction, we will face an ecological collapse that no amount of technology will be able to reverse. Global commons require global governance.",
    ),
    (
        "Deep Ecology and the Rights of Nature",
        "While most environmental policies are anthropocentric-meaning they focus on nature's value to humans-the movement of Deep Ecology argues for the intrinsic value of all living things. This philosophy has led to a revolutionary legal trend: granting legal personhood to rivers, forests, and ecosystems. For example, the Whanganui River in New Zealand and several forests in Colombia now have the same legal rights as a person. Consequently, these ecosystems can be represented in court to stop destructive projects. Furthermore, this shift challenges the idea that nature is merely property for human use. In my view, acknowledging the rights of nature is a necessary step toward a more balanced relationship with our planet. If we continue to view ourselves as masters of the earth rather than part of its complex web of life, we will eventually destroy the very foundations of our own existence.",
    ),
]


ENVIRONMENT_TEXTS["c1"] = [
    (
        "The Anthropocene and the Crisis of Geological Agency",
        "The designation of the Anthropocene as a new geological epoch marks a radical shift in our understanding of the relationship between human history and the Earth's systemic evolution. For the first time, a single species has become a dominant geological force, capable of altering the planet's chemical and biological baseline. The nuance of this paradigm shift lies in the collapse of the traditional distinction between human time and geological time. Our socioeconomic decisions, once considered ephemeral, are now being etched into the lithosphere as permanent stratigraphic markers. Furthermore, the Anthropocene forces us to confront the tragedy of agency; while we have the power to destabilize the climate, our political structures remain woefully inadequate for managing the consequences. We are, in effect, a species with the impact of a meteorite but the governance of a primitive tribe. Averting catastrophe requires an unprecedented synthesis of ethical responsibility and scientific foresight, moving beyond the anthropocentric illusion of total planetary control.",
    ),
    (
        "The Paradox of the Jevons Effect in Sustainable Development",
        "Sustainable development often relies on the promise that technological efficiency will lead to a reduction in resource consumption. However, the Jevons Paradox suggests a far more troubling reality: as the efficiency of a resource increases, its total consumption often rises rather than falls. The nuance of this phenomenon is that efficiency gains lower the relative cost of use, which in turn stimulates demand. For example, as fuel-efficient engines become more common, people tend to drive more frequently or own larger vehicles, effectively negating the environmental benefits. Consequently, a purely technocratic approach to the climate crisis may be inherently flawed if it does not address the underlying logic of infinite economic growth. True sustainability requires not just a greening of our tools, but a radical re-evaluation of our consumption patterns. We must interrogate whether we are using technology to save the planet or merely to sustain a lifestyle that is ecologically untenable.",
    ),
    (
        "Environmental Justice and the Geography of Risk",
        "Environmental degradation is rarely distributed equitably; instead, it tends to follow the fault lines of existing social and economic inequalities. This geography of risk means that marginalized communities are disproportionately exposed to industrial toxins, hazardous waste, and the adverse effects of climate change. The nuance of environmental justice lies in its challenge to the universalist narrative of we are all in this together. While the climate crisis is a global phenomenon, the capacity to adapt is a function of privilege. Furthermore, the externalization of environmental costs by wealthy nations often results in toxic colonialism, where the Global South becomes a dumping ground for the e-waste and industrial byproducts of the North. A C1-level critique must recognize that ecological restoration is inseparable from social reparation. We cannot achieve a green future if that future is built upon the continued exploitation of the vulnerable.",
    ),
    (
        "The Semiotics of Greenwashing in Corporate Discourse",
        "In the contemporary marketplace, green has become a potent semiotic signifier, often detached from any tangible ecological reality. Corporate greenwashing utilizes a sophisticated vocabulary of sustainability, net-zero, and carbon neutrality to create a facade of environmental responsibility while maintaining business-as-usual practices. The nuance of this discourse lies in its ability to co-opt radical language to serve conservative ends. By focusing on individual carbon footprints or symbolic gestures-like banning plastic straws-corporations deflect attention from the systemic destruction caused by industrial-scale extraction and fossil fuel dependency. This creates a state of manufactured confusion, where the consumer is overwhelmed by contradictory claims and vague certifications. To navigate this semiotic minefield, we must move beyond the surface-level rhetoric and demand radical transparency and binding accountability. True sustainability is not a marketing aesthetic; it is a fundamental reconfiguration of the productive apparatus.",
    ),
    (
        "The Epistemology of Climate Skepticism and Disinformation",
        "The persistence of climate skepticism, despite overwhelming scientific consensus, reveals a profound epistemological crisis in the digital age. This skepticism is not merely a lack of information, but a sophisticated product of agnotology-the deliberate manufacture of ignorance. The nuance of this disinformation lies in its mimicry of scientific skepticism; by emphasizing uncertainty and debating the data, fossil fuel interests have successfully delayed political action for decades. Furthermore, the fragmentation of the media landscape allows individuals to retreat into echo chambers that reinforce their existing biases, making the objective truth increasingly difficult to communicate. Addressing the climate crisis, therefore, requires more than just better science; it requires a restoration of public trust in expertise and a critical deconstruction of the political and economic interests that fund the production of doubt. We are fighting not just for the atmosphere, but for the integrity of shared reality.",
    ),
    (
        "Biophilia vs. Biophobia: The Psychological Architecture of the Modern City",
        "E.O. Wilson's biophilia hypothesis suggests that humans possess an innate tendency to seek connections with nature and other forms of life. However, modern urban architecture often fosters a state of biophobia-a profound alienation from the natural world characterized by the sterile dominance of concrete and glass. The nuance of this psychological shift is its impact on human well-being and environmental ethics. When we are disconnected from the rhythmic cycles of the seasons and the complexity of local ecosystems, our capacity for ecological empathy diminishes. This creates a feedback loop of indifference: we do not protect what we do not know, and we do not know what we have systematically excluded from our daily lives. Integrating biophilic design into urban planning-through green corridors, urban forests, and accessible waterways-is not merely an aesthetic choice; it is a psychological necessity. To heal the planet, we must first heal the rift between the human psyche and the biological world it inhabits.",
    ),
    (
        "The Bioethics of Biodiversity Offsetting",
        "Biodiversity offsetting is a market-based conservation tool that allows developers to destroy a habitat in one location, provided they restore or protect an equivalent habitat elsewhere. The nuance of this policy is its reductionist view of ecology; it assumes that complex, ancient ecosystems are fungible or replaceable assets. A C1-level analysis must interrogate whether a centuries-old forest can ever be truly compensated for by a new, mono-cultural plantation. Furthermore, this no net loss philosophy often ignores the unique cultural and spiritual significance of specific landscapes to local communities. The ethical danger of offsetting is that it turns nature into a tradable commodity, potentially legitimizing the destruction of the irreplaceable under the guise of an accounting trick. True conservation must prioritize the intrinsic value of place, recognizing that some ecosystems are simply too vital-and too unique-to be sacrificed at the altar of development.",
    ),
    (
        "The Tragedy of the Commodity: Capitalism and Ecological Collapse",
        "The Tragedy of the Commons is frequently cited as the primary driver of environmental degradation, but many scholars argue that the true culprit is the Tragedy of the Commodity. This critique suggests that the inherent drive of capitalism for infinite expansion on a finite planet is ecologically impossible. The nuance of this perspective is that the market treats the environment as both an infinite source of raw materials and an infinite sink for waste. Because capital must constantly circulate and grow, it inevitably exceeds the planetary boundaries that sustain life. Consequently, green capitalism may be an oxymoron if it does not challenge the imperative of compound growth. A transition to a truly sustainable society would require a move toward degrowth or steady-state economics-a paradigm where human well-being is decoupled from material throughput. This is not just a technical challenge, but a profound philosophical shift in how we define progress.",
    ),
    (
        "The Ethics of Geoengineering: Playing God with the Atmosphere",
        "As the window for limiting global warming to 1.5 degrees Celsius closes, the prospect of solar geoengineering-injecting aerosols into the stratosphere to reflect sunlight-is moving from the margins to the center of climate debate. The nuance of this technological fix lies in its profound moral hazard: if we believe a technical solution exists to cool the planet, will we lose the political will to reduce carbon emissions? Furthermore, the potential unintended consequences are staggering, including shifts in global monsoon patterns and the disruption of local agriculture. The governance of such technology presents an unprecedented challenge: who has the right to control the global thermostat? A C1-level ethical framework must recognize that geoengineering is not a solution, but a desperate and dangerous gamble. We are contemplating an intervention into a system so complex that our models may never be able to fully predict the cascading failures that could follow.",
    ),
    (
        "Deep Time and the Ethics of Nuclear Waste",
        "The management of high-level nuclear waste presents one of the most significant ethical challenges in human history, requiring us to think in terms of deep time. Some isotopes remain hazardous for hundreds of thousands of years-a duration that far exceeds the lifespan of any human civilization or language. The nuance of this challenge lies in our responsibility to a deep future that we cannot possibly imagine. How do we design markers or warning systems that will remain intelligible to beings living 100,000 years from now? Furthermore, the decision to generate such waste is a form of intergenerational tyranny, where we enjoy the benefits of energy today while bequeathing the risks to thousands of future generations. This forced temporal inheritance highlights the limits of our current political and ethical frameworks, which are almost entirely focused on the short term. To live ethically in the nuclear age is to recognize our role as ancestors to a future that we are currently endangering.",
    ),
]


ENVIRONMENT_TEXTS["c2"] = [
    (
        "The Elegiac Landscape: Aesthetics of the Vanishing World",
        "To witness the contemporary natural world is to engage in a sustained act of mourning, a process of traversing what can only be described as an elegiac landscape. The nuance of this aesthetic experience lies in the tension between the residual beauty of the earth and the omnipresent specter of its degradation. When we contemplate a melting glacier or a bleaching coral reef, we are not merely observing a biological failure; we are witnessing the dissolution of a temporal sanctuary. This sublime of the void differs from the Romantic sublime, which found terror in nature's power; the modern sublime finds terror in nature's fragility. Our relationship with the environment has become a hauntology, where every forest and river is haunted by the ghost of its own future absence. To live ethically in such a landscape requires a radical vulnerability-a willingness to love that which is already slipping through our fingers, acknowledging that the act of witnessing is, in itself, a form of resistance against indifference.",
    ),
    (
        "The Telos of the Technosphere: Biology in the Age of Silicon",
        "The emergence of the technosphere-the global, integrated system of technological artifacts and infrastructures-presents a fundamental challenge to the traditional telos of biological life. We are currently navigating a transition where the metabolic requirements of the industrial machine are beginning to override the regenerative cycles of the biosphere. The nuance of this shift is the instrumentalization of the organic; we no longer view a forest as a self-contained teleological entity, but as a resource bank to be managed by algorithmic precision. This creates a state of biological alienation, where the human organism is increasingly mediated by silicon interfaces, distancing us from the visceral realities of soil and rot. A C2-level meditation must ask whether the technosphere is a natural evolutionary extension of the human mind or a parasitic entity that is slowly hollowing out its biological host. If the destination of technology is total efficiency, then the inherent messiness of life-extinction, decay, and spontaneous growth-becomes a bug to be programmed out of existence.",
    ),
    (
        "The Metaphysics of Extinction: On the Silence of the Species",
        "Extinction is often framed as a biological statistic, a ledger of loss recorded in the cold archives of paleontology. However, the true weight of extinction is metaphysical-it is the permanent silencing of a unique way of being in the world. Every species represents a specific evolutionary conversation with the environment, a linguistic structure encoded in DNA and behavior that has been refined over eons. The nuance of this loss is the ontological thinning of the planet; with every disappearing lineage, the tapestry of reality becomes less complex, less vibrant, and more monotonous. We are moving toward a monoculture of the spirit, where the diversity of life is replaced by the sterile sameness of the human-dominated landscape. To confront extinction is to acknowledge our role as the unwitting executioners of our own biological kin, a realization that demands a profound shift in our ethical horizon. We must move beyond a morality of utility toward a morality of reverence, recognizing that the right to exist is not something we have the authority to grant or revoke.",
    ),
    (
        "The Gaia Hypothesis and the Dialectics of Planetary Homeostasis",
        "James Lovelock's Gaia Hypothesis-the proposal that the Earth functions as a self-regulating, synergistic organism-remains one of the most provocative and misunderstood concepts in modern ecology. The nuance of this dialectic is the realization that life is not merely an inhabitant of the planet, but its primary architect. The atmosphere, the oceans, and the crust are not static backdrops but active physiological components of a planetary homeostasis. However, the tragedy of the Anthropocene is that human activity has disrupted these feedback loops, pushing the system toward a tipping point beyond which a new, far less hospitable equilibrium may emerge. This suggests that Gaia is not a benevolent mother who will protect us, but a rigorous biological system that may ultimately find our presence incompatible with its own survival. To live in harmony with Gaia is to accept our status as a sub-system of a larger whole, abandoning the hubris of the master for the humility of the participant.",
    ),
    (
        "The Aesthetics of the Ruin: Nature's Reclamative Power",
        "There is a profound, almost theological beauty in the aesthetics of the ruin-the sight of nature slowly reclaiming the abandoned infrastructures of industrial civilization. Whether it is a vine strangling a concrete pillar or a forest growing through the floor of a derelict factory, these images serve as a memento mori for the technocratic dream. The nuance of this reclamation is the unfolding of the artificial; it reveals that our structures are merely temporary interruptions in a much longer biological narrative. The ruin is the site where human history and natural history collide, creating a liminal zone where the distinction between the made and the grown begins to blur. This process of decay is not a failure, but a return to a deeper, more resilient order. In the ruin, we find hope: the assurance that even after the collapse of our complex systems, the earth will continue its quiet, relentless work of regeneration.",
    ),
    (
        "The Ethics of the Last Man: Responsibility at the End of History",
        "The thought experiment of the Last Man-the final human being alive on Earth-serves as a critical tool for exploring the intrinsic value of the environment. If there were no one left to appreciate a sunset or benefit from a forest, would those things still possess value? The nuance of this ethical inquiry is the rejection of subjective instrumentalism. A C2-level perspective argues that the value of the biosphere is not contingent upon human perception; it is an objective property of life's inherent complexity and striving. Consequently, our current destruction of the environment is a crime not just against future generations of humans, but against the integrity of the cosmos itself. We must act as if we are the custodians of the absolute, recognizing that our responsibility to the planet transcends our own species' survival. The Last Man reminds us that we are part of a narrative that existed long before our arrival and should continue long after our departure.",
    ),
    (
        "The Semiotics of the Wilderness: Deconstructing the Primal",
        "The concept of wilderness is often romanticized as a pristine, untouched realm of primal purity. However, a sophisticated deconstruction reveals that wilderness is, in part, a cultural construct-a semiotic void onto which we project our own desires for innocence and escape. The nuance of this realization is that by designating certain areas as wild, we inadvertently legitimize the total industrialization of everything else. This dualism of space separates humanity from nature, creating a psychological barrier that prevents us from seeing the wildness in our own backyards. True ecology requires the dismantling of this binary, acknowledging that nature is everywhere-in the cracks of the sidewalk as much as in the heart of the Amazon. We must move toward an integrated landscape where human habitation and biological complexity are seen as mutually reinforcing rather than mutually exclusive. The wilderness is not a place you go to; it is a quality of life that we must cultivate in every square meter of our existence.",
    ),
    (
        "The Phenomenology of the Storm: Nature as a Transcendent Force",
        "In the age of meteorological modeling and satellite tracking, we have attempted to domesticate the storm, turning it into a predictable data set. Yet, when we stand in the path of a truly powerful atmospheric event, the phenomenology of the experience remains one of overwhelming otherness. The nuance of the storm is its indifference; it is a visceral demonstration of a force that operates entirely outside the human moral or political framework. In the roaring wind and the torrential rain, we encounter the radical outside-a power that reminds us of our own precariousness. This encounter is a necessary corrective to our technological hubris. It forces a state of existential humility, where we recognize that despite our sophisticated systems of control, we remain subject to the primal ebbs and flows of a planetary system that is vast, ancient, and ultimately untamable. The storm is not an enemy to be defeated, but a sovereign to be respected.",
    ),
    (
        "The Ethics of the Slow Catastrophe: Perception and the Time of Ecology",
        "The greatest challenge of the climate crisis is that it functions as a slow catastrophe, a gradual accumulation of incremental changes that elude the urgency of human perception. Our brains are evolved to respond to sudden, visceral threats-the predator in the grass or the sudden fire-but we are ill-equipped to perceive the decadal rise of sea levels or the subtle shift in migratory patterns. The nuance of this perceptual gap is that by the time the catastrophe becomes visible to the senses, it is often already irreversible. To live ethically in the Anthropocene is to develop a temporal imagination that can bridge the gap between our daily lives and the deep time of the planet. We must learn to read the silence of the disappearing insects and the syntax of the warming oceans as an emergency siren that has been blaring for decades. Responsibility requires that we act on what we know, even when our senses tell us that everything is normal.",
    ),
    (
        "The Alchemical Earth: Transmutation, Waste, and the Cycle of Being",
        "From a C2-level perspective, the Earth is a vast alchemical vessel where matter is constantly being transmuted through the cycles of life, death, and mineralization. The concept of waste is a human error-a failure of imagination. In the biological world, the byproduct of one process is always the substrate for another. The nuance of this alchemical cycle is that our own bodies are merely temporary arrangements of ancient atoms that have traveled through countless other forms. This realization fosters a sense of radical kinship with the earth; we are not on the planet, we are of it. To treat the environment as a dump is to fail to understand the fundamental law of the conservation of being. Our goal should be to realign our industrial processes with this circular alchemy, ensuring that every end is a new beginning. In the end, we do not save the planet; we simply learn to participate in its eternal, self-sustaining dance of transformation.",
    ),
]


LEVEL_NOTES = {
    "iniciante": "presente simples, estruturas de repeticao e vocabulario concreto",
    "a1": "conservacao, conectores simples, presente continuo e futuro com going to",
    "a2": "passado simples, comparativos e descricoes de mudancas ambientais",
    "b1": "opinioes, argumentacao, causa e consequencia, conectores variados",
    "b2": "analise de politicas, ciencia, etica e vocabulario tecnico",
    "c1": "analise critica e sistemica, nuance filosofica e registros formais",
    "c2": "estetica, filosofia, ambiguidade poetica e registros literarios densos",
}


class Command(BaseCommand):
    help = "Replace the Meio ambiente catalog with 70 curated leveled texts, 10 per level."

    def add_arguments(self, parser):
        parser.add_argument("--skip-assets", action="store_true")
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        category = Category.objects.get(slug="meio-ambiente")
        total = 0
        range_warnings = []

        for level in Level.objects.order_by("order"):
            entries = ENVIRONMENT_TEXTS[level.slug]
            existing = list(Text.objects.filter(category=category, level=level).order_by("id"))

            for index, (title, content) in enumerate(entries, start=1):
                words = readable_word_count(content)
                min_words, max_words = LEVEL_WORD_LIMITS[level.slug]
                if not (min_words <= words <= max_words):
                    range_warnings.append(f"{level.slug} #{index}: {words} words")

                text = existing[index - 1] if index <= len(existing) else Text()
                text.slug = slugify(f"{level.slug}-meio-ambiente-{index:02d}-{title}")
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

        self.stdout.write(self.style.SUCCESS(f"Updated {total} Meio ambiente texts."))

    def summary_for(self, level, title, content):
        note = LEVEL_NOTES[level.slug]
        first_sentence = content.split(".")[0].strip()
        return f"Texto em ingles sobre meio ambiente: {title}. Nivel {level.name}, com {note}. Tema central: {first_sentence}."

    def prompt_for(self, level, category, title, content):
        scene = content.split(".")[0].strip()
        return (
            "Digital art, 2D cartoon style, clean lines, high quality, "
            f"educational environmental scene about {title}, showing {scene}, "
            "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, "
            f"category {category.name}, level {level.name}, no text, no copyright infringement"
        )


def readable_word_count(value):
    return len(READABLE_WORD_RE.findall(value or ""))
