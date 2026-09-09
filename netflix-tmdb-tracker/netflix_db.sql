-- ============================================
-- Base de datos: catálogo de Netflix (vía TMDb)
-- ============================================

CREATE DATABASE IF NOT EXISTS netflix_catalog
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE netflix_catalog;

-- Tabla principal de títulos (películas y series)
CREATE TABLE IF NOT EXISTS titulos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmdb_id INT NOT NULL,
    tipo ENUM('movie', 'tv') NOT NULL,
    titulo VARCHAR(500) NOT NULL,
    titulo_original VARCHAR(500),
    sinopsis TEXT,
    fecha_estreno DATE,
    idioma_original VARCHAR(10),
    popularidad DECIMAL(10,3),
    rating_promedio DECIMAL(4,2),
    cantidad_votos INT,
    poster_path VARCHAR(255),
    pais_disponible VARCHAR(5) NOT NULL DEFAULT 'AR',
    fecha_scrapeo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unico_tmdb_pais (tmdb_id, tipo, pais_disponible)
) ENGINE=InnoDB;

-- Tabla de géneros
CREATE TABLE IF NOT EXISTS generos (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- Relación muchos a muchos: títulos <-> géneros
CREATE TABLE IF NOT EXISTS titulo_genero (
    titulo_id INT NOT NULL,
    genero_id INT NOT NULL,
    PRIMARY KEY (titulo_id, genero_id),
    FOREIGN KEY (titulo_id) REFERENCES titulos(id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id) REFERENCES generos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Índices útiles
CREATE INDEX idx_tipo ON titulos(tipo);
CREATE INDEX idx_titulo ON titulos(titulo);
CREATE INDEX idx_fecha_estreno ON titulos(fecha_estreno);
