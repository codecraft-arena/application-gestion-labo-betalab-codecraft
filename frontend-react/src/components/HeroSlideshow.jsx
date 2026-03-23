/**
 * Diaporama hero avec effet Ken Burns (zoom + fondu).
 * Affiche 5 images locales (/lab1-5.jpg) en rotation toutes les 6 secondes.
 * Utilisé dans la section hero de chaque page du site.
 */
import { useState, useEffect } from "react";
import "./HeroSlideshow.css";

const defaultImages = [
  {
    url: "/lab1.jpg",
    alt: "Recherche en laboratoire informatique",
  },
  {
    url: "/lab2.jpg",
    alt: "Circuit imprimé et technologie",
  },
  {
    url: "/lab3.jpg",
    alt: "Cybersécurité et réseaux",
  },
  {
    url: "/lab4.jpg",
    alt: "Programmation et développement",
  },
  {
    url: "/lab5.jpg",
    alt: "Espace de travail collaboratif tech",
  },
];

export default function HeroSlideshow({ images = defaultImages }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % images.length);
    }, 6000);
    return () => clearInterval(timer);
  }, [images.length]);

  return (
    <div className="hero-slideshow" aria-hidden="true">
      {images.map((img, i) => (
        <div key={i} className={`hero-slide ${i === current ? "active" : ""}`}>
          <img src={img.url} alt={img.alt} />
        </div>
      ))}
      <div className="hero-slideshow-overlay" />
    </div>
  );
}
