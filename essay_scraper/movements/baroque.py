from essay_scraper.essay_model import EssayResponse,EssayCategory
from essay_scraper.movements.common import divide_str_into_managable_chunks


def get_movement_essays()->list[EssayResponse]:
    libre_texts_chunks = []
    divide_str_into_managable_chunks(data=[
        """The Baroque is a period of artistic style that started around 1600 in Rome , Italy, and spread throughout the majority of Europe during the 17th and 18th centuries. In informal usage, the word baroque describes something that is elaborate and highly detailed.The most important factors during the Baroque era were the Reformation and the Counter-Reformation, with the development of the Baroque style considered to be linked closely with the Catholic Church. The popularity of the style was in fact encouraged by the Catholic Church, which had decided at the Council of Trent that the arts should communicate religious themes and direct emotional involvement in response to the Protestant Reformation. Baroque art manifested itself differently in various European countries owing to their unique political and cultural climates.""",
        """The Baroque style is characterized by exaggerated motion and clear detail used to produce drama, exuberance, and grandeur in sculpture, painting, architecture, literature, dance, and music. Baroque iconography was direct, obvious, and dramatic, intending to appeal above all to the senses and the emotions. The use of the chiaroscuro technique is a well known trait of Baroque art. This technique refers to the interplay between light and dark and is often used in paintings of dimly lit scenes to produce a very high-contrast, dramatic atmosphere. The chiaroscuro technique is visible in the painting The Massacre of the Innocents by Peter Paul Rubens. Other important Baroque painters include Caravaggio (who is thought to be a precursor to the movement and is known for work characterized by close-up action and strong diagonals) and Rembrandt."""
    ], chunks=libre_texts_chunks)

    vault_editions_movement_chunks = []
    divide_str_into_managable_chunks(data=[
        """One of the most prominent characteristics of Baroque art is its penchant for dramatic realism. Artists of this period aimed to evoke strong emotional responses in viewers by portraying subjects in vivid scenes full of movement. This realism extended to both the human form and the natural world. Figures in Baroque paintings and sculptures exhibit a heightened sense of emotion, their expressions and gestures conveying drama and power""",        
    ], chunks=vault_editions_movement_chunks)

    
    vault_editions_technique_chunks = []

    divide_str_into_managable_chunks(data=[
        """One of the most prominent characteristics of Baroque art is its penchant for dramatic realism. Artists of this period aimed to evoke strong emotional responses in viewers by portraying subjects in vivid scenes full of movement. This realism extended to both the human form and the natural world. Figures in Baroque paintings and sculptures exhibit a heightened sense of emotion, their expressions and gestures conveying drama and power.""",
        """Baroque artists typically used a vibrant colour palette to heighten the sense of drama in their paintings. Artists used deep reds, velvety blues, lush greens, and sumptuous gold to evoke emotion and create a sense of power and awe. They also used the chiaroscuro technique, where deep shadows and light created striking contrasts that heightened the overall impact of their compositions. Baroque painters guided the viewer's gaze by strategically placing shadows to obscure and reveal different parts of their subjects. Artists wanted to evoke a sense of movement as if their subjects were caught in a moment of action or contemplation. Chiaroscuro gave Baroque art its distinctive sense of tension, energy, and emotional intensity, making it a hallmark of the period's artistic legacy""",
        """An obsession with ornate detailing and opulence marked the Baroque period. Artists and artisans utilised expensive materials like marble, lacquer, gold and glass and added elaborate decorations and intricate patterns to embellish their works. Baroque artists created intricate creations full of detail, from complex stucco work and ornate frames to emotive trompe l'oeil paintings of heavenly scenes on the ceiling of churches. Typical motifs included fruits, sea shells, flowers, foliage, curving waves, religious and mythological elements and fantastical birds and beasts."""
    ], chunks=vault_editions_technique_chunks)

    vault_editions_genre_chunks = []

    divide_str_into_managable_chunks(data=[
        """After the Protestant Reformation, the Catholic Church turned to Baroque art to rekindle its followers' spiritual fervour and inspire deep devotion and connection with the divine. By commissioning elaborate religious paintings, sculptures, and ornate decorations for churches and cathedrals, the Church sought to create immersive and awe-inspiring environments that elicit a strong emotional response from worshipers. These artworks depicted vivid scenes from the Bible, the lives of saints, and the grandeur of the Church, inviting believers to re-engage with their faith on a profound level"""
        ], chunks=vault_editions_genre_chunks)

    virtual_instructor_technique_chunks = []
    divide_str_into_managable_chunks(data=[
        """During the Baroque period, most artists used canvases or panels that were toned dark brown and even black. There are some great advantages to working over a dark base layer which cannot be replicated by working on a light ground.The greatest benefit to working on a dark canvas is that it saves effort. All of the shadows are already there. The artist simply needs to focus on the light values. This approach to painting is very similar to working on a black drawing surface with a white drawing medium. The shadows are either ignored or completed using a technique called scumbling. Scumbling is a painting technique in which a thin, translucent application of paint is vigorously scrubbed into the canvas, while allowing part of the layer underneath to show through.A finished Baroque painting feels sculptural because the light areas stand out in relief compared to the extremely thin application of paint in the shadows. Since the shades are created through an optical mixture of translucent color over the dark, dull surface, the shadows are never that colorful. If you prefer brighter, high-key paintings then this characteristic of Baroque painting would be a drawback. However, because the shadows are so dull, the lights seem brighter by contrast."""],
        chunks=virtual_instructor_technique_chunks)



    result:list[EssayResponse] = [
        {
            'chunks': libre_texts_chunks,
            'essay_title':'The Baroque Period',
            'essay_type': EssayCategory.MOVEMENT,
            'source' : 'Libre Texts Humanities',
            'source_url':'https://human.libretexts.org/Bookshelves/Art/Art_History_(Boundless)/21%3A_The_Baroque_Period/21.01%3A_The_Baroque_Period'
        },
        {
            'chunks':vault_editions_movement_chunks,
            'essay_title':'An Introduction to Baroque Art',
            'essay_type': EssayCategory.MOVEMENT,
            'source' : 'Vault Editions',
            'source_url':'https://vaulteditions.com/blogs/news/discover-five-characteristics-of-baroque-art'
        },
        {
            'chunks' : vault_editions_technique_chunks,
            'essay_title': 'Characteristics of Baroque Art',
            'essay_type' : EssayCategory.TECHNIQUE,
            'source' : 'Vault Editions',
            'source_url':'https://vaulteditions.com/blogs/news/discover-five-characteristics-of-baroque-art'
        },

        {
            'chunks' : vault_editions_genre_chunks,
            'essay_title': 'Characteristics of Baroque Art',
            'essay_type':EssayCategory.GENRE,
            'source' : 'Vault Editions',
            'source_url':'https://vaulteditions.com/blogs/news/discover-five-characteristics-of-baroque-art'
        },

        {
            'chunks': virtual_instructor_technique_chunks,
            'essay_title': 'Special Baroque Painting Technique',
            'essay_type' : EssayCategory.TECHNIQUE,
            'source' : 'Virtual Instructor',
            'source_url': 'https://thevirtualinstructor.com/blog/baroque-painting-technique'
        }

    ]   




    return result
