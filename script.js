document.addEventListener('DOMContentLoaded', () => {
    const projectGrid = document.getElementById('project-grid');
    const illustrationsGrid = document.getElementById('illustrations-grid');
    const croquisGrid = document.getElementById('croquis-grid');

    if (projectGrid) {
        loadProjects();
    }

    if (illustrationsGrid) {
        loadIllustrations();
    }

    if (croquisGrid) {
        loadCroquis();
    }
});

async function loadCroquis() {
    try {
        const response = await fetch('croquis.json');
        const croquis = await response.json();
        const grid = document.getElementById('croquis-grid');

        for (const item of croquis) {
            const card = document.createElement('div');
            card.className = 'project-wrapper';
            card.id = `card-croquis-${item.id}`;
            
            const coverPath = `image/${item.folder}/${item.cover || 'cover.jpg'}`;
            
            card.innerHTML = `
                <h3 class="project-title-visible">${item.title}</h3>
                <div class="project-card" onclick="openProjectModal('${item.id}')">
                    <img src="${coverPath}" alt="${item.title}" onerror="this.src='image/placeholder.jpg'">
                    <div class="project-info">
                        <h3 class="project-title">Voir le carnet</h3>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        }
        
        // Add croquis to global projectsData so modal works
        window.projectsData = (window.projectsData || []).concat(croquis);

    } catch (error) {
        console.error('Error loading croquis:', error);
    }
}

async function loadProjects() {
    try {
        const response = await fetch('projects.json');
        const projects = await response.json();
        const grid = document.getElementById('project-grid');

        for (const project of projects) {
            const card = document.createElement('div');
            card.className = 'project-wrapper';
            card.id = `card-project-${project.id}`;
            
            // Determine cover image path
            // Assuming cover is inside the project folder
            const coverPath = `image/${project.folder}/${project.cover || 'cover.jpg'}`;
            
            card.innerHTML = `
                <h3 class="project-title-visible">${project.title}</h3>
                <div class="project-card" onclick="openProjectModal('${project.id}')">
                    <img src="${coverPath}" alt="${project.title}" onerror="this.src='image/placeholder.jpg'">
                    <div class="project-info">
                        <h3 class="project-title">Voir le projet</h3>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        }
        
        // Store projects globally for modal access
        window.projectsData = projects;

    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function openProjectModal(projectId) {
    const project = window.projectsData.find(p => p.id === projectId);
    if (!project) return;

    const modal = document.getElementById("projectModal");
    const modalBody = document.getElementById("modalBody");
    
    // Fetch description
    let description = '';
    try {
        const descResponse = await fetch(`image/${project.folder}/description.txt`);
        if (descResponse.ok) {
            description = await descResponse.text();
        } else {
            description = "Description non disponible.";
        }
    } catch (e) {
        description = "Erreur lors du chargement de la description.";
    }

    // Build Modal Content
    let content = `
        <div style="text-align: center; margin-bottom: 3rem;">
            <h2 style="font-family: var(--font-artistic); font-size: 2.5rem; color: var(--primary-color); margin-bottom: 1rem; text-transform: uppercase;">${project.title}</h2>
    `;

    // Featured Video (YouTube)
    if (project.youtube_id) {
        content += `
            <div style="width: 100%; max-width: 900px; margin: 2rem auto; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                <iframe 
                    src="https://www.youtube.com/embed/${project.youtube_id}" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    allowfullscreen>
                </iframe>
            </div>
        `;
    }

    content += `
            <p style="color: #333; font-size: 1.1rem; max-width: 800px; margin: 0 auto; line-height: 1.8; white-space: pre-wrap;">${description}</p>
        </div>
    `;

    // Gallery
    if (project.images && project.images.length > 0) {
        content += `<div class="project-detail-grid">`;
        project.images.forEach(img => {
            const imgPath = `image/${project.folder}/${img}`;
            content += `
                <div class="project-detail-item">
                    <img src="${imgPath}" alt="${project.title}" style="width: 100%; display: block; cursor: pointer;" onclick="openLightbox('${imgPath}')">
                </div>
            `;
        });
        content += `</div>`;
    }

    modalBody.innerHTML = content;
    modal.style.display = "block";
    document.body.style.overflow = "hidden";
}

function closeModal() {
    document.getElementById("projectModal").style.display = "none";
    document.body.style.overflow = "auto";
}

// Illustrations Logic
async function loadIllustrations() {
    try {
        const response = await fetch('illustrations.json');
        const images = await response.json();
        const grid = document.getElementById('illustrations-grid');
        
        window.illustrationImages = images;

        images.forEach((imgUrl, index) => {
            const item = document.createElement('div');
            item.className = 'masonry-item';
            item.onclick = () => openImage(index);
            item.innerHTML = `<img src="${imgUrl}" alt="Illustration">`;
            grid.appendChild(item);
        });

    } catch (error) {
        console.error('Error loading illustrations:', error);
    }
}

// Illustration Modal Logic
let currentIllustrationIndex = 0;

function openImage(index) {
    currentIllustrationIndex = index;
    const modal = document.getElementById("imageModal");
    modal.style.display = "flex";
    modal.style.alignItems = "center";
    modal.style.justifyContent = "center";
    updateImage();
    document.body.style.overflow = "hidden";
}

function closeImageModal() {
    document.getElementById("imageModal").style.display = "none";
    document.body.style.overflow = "auto";
}

function changeImage(n) {
    const images = window.illustrationImages;
    currentIllustrationIndex += n;
    if (currentIllustrationIndex >= images.length) {
        currentIllustrationIndex = 0;
    } else if (currentIllustrationIndex < 0) {
        currentIllustrationIndex = images.length - 1;
    }
    updateImage();
}

function updateImage() {
    const images = window.illustrationImages;
    const modalImg = document.getElementById("fullImage");
    modalImg.src = images[currentIllustrationIndex];
}

// Lightbox Logic (for Projects)
function openLightbox(src) {
    const modal = document.getElementById("lightboxModal");
    const modalImg = document.getElementById("lightboxImage");
    modal.style.display = "flex";
    modal.style.alignItems = "center";
    modal.style.justifyContent = "center";
    modalImg.src = src;
}

function closeLightbox() {
    document.getElementById("lightboxModal").style.display = "none";
}

// Close modals on outside click
window.onclick = function(event) {
    const projectModal = document.getElementById("projectModal");
    const lightboxModal = document.getElementById("lightboxModal");
    const imageModal = document.getElementById("imageModal");
    
    if (event.target == projectModal) closeModal();
    if (event.target == lightboxModal) closeLightbox();
    if (event.target == imageModal) closeImageModal();
}
