from essay_scraper.essay_model import EssayResponse, EssayCategory
from essay_scraper.movements.common import divide_str_into_managable_chunks


def get_cubism_essays()->list[EssayResponse]:

    tate_org_movement_chunks = []
    divide_str_into_managable_chunks(
        data=["""In around 1907 two artists living in Paris called Pablo Picasso and Georges Braque developed a revolutionary new style of painting which transformed everyday objects, landscapes, and people into geometric shapes. In 1908 art critic Louis Vauxcelles, saw some landscape paintings by Georges Braque (similar to the picture shown above) in an exhibition in Paris, and described them as ‘bizarreries cubiques’ which translates as ‘cubist oddities’ – and the term cubism was coined."""        ],
        chunks=tate_org_movement_chunks
    )

    tate_org_technique_chunks = []
    divide_str_into_managable_chunks(
        data=["""The Cubist felt that they could give the viewer a more accurate understanding of an object, landscape or person by showing it from different angles or viewpoints, so they used flat geometric shapes to represent the different sides and angles of the objects. By doing this, they could suggest three-dimensional qualities and structure without using techniques such as perspective and shading. This breaking down of the real world into flat geometric shapes also emphasized the two-dimensional flatness of the canvas. This suited the cubists’ belief that a painting should not pretend to be like a window onto a realistic scene but as a flat surface it should behave like one."""],
        chunks=tate_org_technique_chunks
    )


    mont_marte_technique_chunks = []
    divide_str_into_managable_chunks(
        data=[
            """The Cubists focused a lot on shapes in their artworks, so they often painted objects like musical instruments, bottles, glasses, newspapers and human figures. To create in the Cubist style, play around with subjects that have interesting shapes to them like a quirky still life or try a Cubism self-portrait.""",
            """Everyone has probably seen Pablo Picasso’s quirky artworks like The Weeping Woman and you might have noticed the different perspectives that come together to make the fragmented face. Cubists used multiple perspectives when creating their objects and didn’t add in any foreshortening or shading for dimension, this gave Cubism that abstract look.""",
            """One of the most well-known Cubism techniques is the use of geometric shapes. Both artists, Georges Braque and Pablo Picasso used a mix of shapes to show form in their art. Another technique in Cubism, is the use of sharp lines, this helped add to the 2D look of flatness in their artworks""",
            """When it comes to Cubist painting techniques, dipping into a monochromatic palette is key. A lot of Cubist paintings use grey, ochre, black or muted tones like blues or greens. This was because a muted colour palette gave more emphasis on the subject and didn’t distract the viewer with bright bursts of colour.""",
        ],
        chunks=mont_marte_technique_chunks
    )

    result:list[EssayResponse] = [
        {
            'chunks': tate_org_movement_chunks, 
            'essay_title' : 'Cubism', 
            'essay_type':EssayCategory.MOVEMENT, 
            'source': "Tate org", 
            'source_url': 'https://www.nga.gov/artworks/cubism'
        },
        {
            'chunks': tate_org_technique_chunks, 
            'essay_title' : 'Techniques in Cubism', 
            'essay_type':EssayCategory.TECHNIQUE, 
            'source': "Tate org", 
            'source_url': 'https://www.nga.gov/artworks/cubism'

        },
        {
            'chunks': mont_marte_technique_chunks,
            'source': 'Mont Marte', 
            'source_url':'https://www.montmarte.com/blogs/tips-techniques/cubism-techniques',
            'essay_title':'Cubism Techniques',
            'essay_type': EssayCategory.TECHNIQUE
        }
    ]




    return result