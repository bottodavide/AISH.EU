/**
 * Banner Hero Component
 * Descrizione: Banner dinamico hero per homepage
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import apiClient from '@/lib/api-client';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Banner {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  image_url?: string;
  video_url?: string;
  cta_text?: string;
  cta_link?: string;
  cta_variant: string;
  position: string;
  display_order: number;
  background_color?: string;
  text_color?: string;
  is_active: boolean;
}

interface BannersResponse {
  banners: Banner[];
  total: number;
}

export function BannerHero() {
  const [banners, setBanners] = useState<Banner[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadBanners();
  }, []);

  // Auto-advance slider
  useEffect(() => {
    if (banners.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % banners.length);
    }, 5000); // Change every 5 seconds

    return () => clearInterval(interval);
  }, [banners.length]);

  const loadBanners = async () => {
    setIsLoading(true);

    try {
      const response = await apiClient.get<BannersResponse>('/homepage/banners', {
        params: {
          position: 'hero',
          active_only: true,
          page_size: 5,
        },
      });

      setBanners(response.banners || []);
    } catch (err: any) {
      // Gestione errore 404: nessun banner disponibile
      if (err.response?.status === 404) {
        console.log('No hero banners found, showing fallback');
        setBanners([]);
      } else {
        // Altri errori (rete, server, ecc.)
        console.error('Failed to load hero banners:', err);
        setBanners([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const nextBanner = () => {
    setCurrentIndex((prev) => (prev + 1) % banners.length);
  };

  const prevBanner = () => {
    setCurrentIndex((prev) => (prev - 1 + banners.length) % banners.length);
  };

  // Se non ci sono banner, mostra hero statico di fallback
  if (!isLoading && banners.length === 0) {
    return (
      <section className="relative py-20 lg:py-32 bg-gradient-to-b from-background to-muted">
        <div className="container">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl mb-6">
              Innovazione AI in Sicurezza e Compliance
            </h1>
            <p className="text-xl text-muted-foreground mb-8">
              Consulenza strategica per aziende che vogliono adottare l'Intelligenza Artificiale
              rispettando GDPR, NIS2 e normative di Cybersecurity
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link href="/servizi">
                <Button size="lg">Scopri i Servizi</Button>
              </Link>
              <Link href="/contatti">
                <Button size="lg" variant="outline">
                  Contattaci
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <section className="relative py-20 lg:py-32 bg-gradient-to-b from-background to-muted">
        <div className="container">
          <div className="mx-auto max-w-4xl text-center">
            <div className="animate-pulse space-y-4">
              <div className="h-12 bg-muted-foreground/20 rounded w-3/4 mx-auto"></div>
              <div className="h-6 bg-muted-foreground/20 rounded w-2/3 mx-auto"></div>
              <div className="h-6 bg-muted-foreground/20 rounded w-2/3 mx-auto"></div>
            </div>
          </div>
        </div>
      </section>
    );
  }

  const currentBanner = banners[currentIndex];

  // Dynamic banner from CMS
  return (
    <section
      className="relative py-20 lg:py-32 overflow-hidden"
      style={{
        backgroundColor: currentBanner.background_color || undefined,
        color: currentBanner.text_color || undefined,
      }}
    >
      {/* Background Image/Video */}
      {currentBanner.image_url && !currentBanner.video_url && (
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: `url(${currentBanner.image_url})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: 0.3,
          }}
        />
      )}

      {currentBanner.video_url && (
        <video
          className="absolute inset-0 w-full h-full object-cover z-0 opacity-30"
          autoPlay
          muted
          loop
          playsInline
        >
          <source src={currentBanner.video_url} type="video/mp4" />
        </video>
      )}

      {/* Content */}
      <div className="container relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl mb-6 animate-fade-in">
            {currentBanner.title}
          </h1>

          {currentBanner.subtitle && (
            <p className="text-xl mb-4 font-semibold">
              {currentBanner.subtitle}
            </p>
          )}

          {currentBanner.description && (
            <p className="text-lg opacity-90 mb-8">
              {currentBanner.description}
            </p>
          )}

          {currentBanner.cta_text && currentBanner.cta_link && (
            <div className="flex justify-center">
              <Link href={currentBanner.cta_link}>
                <Button
                  size="lg"
                  variant={
                    currentBanner.cta_variant === 'primary'
                      ? 'default'
                      : currentBanner.cta_variant === 'secondary'
                      ? 'secondary'
                      : 'outline'
                  }
                >
                  {currentBanner.cta_text}
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Arrows (if multiple banners) */}
      {banners.length > 1 && (
        <>
          <button
            onClick={prevBanner}
            className="absolute left-4 top-1/2 -translate-y-1/2 z-20 p-2 rounded-full bg-background/50 hover:bg-background/80 transition-colors"
            aria-label="Previous banner"
          >
            <ChevronLeft className="h-6 w-6" />
          </button>
          <button
            onClick={nextBanner}
            className="absolute right-4 top-1/2 -translate-y-1/2 z-20 p-2 rounded-full bg-background/50 hover:bg-background/80 transition-colors"
            aria-label="Next banner"
          >
            <ChevronRight className="h-6 w-6" />
          </button>

          {/* Dots Indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex gap-2">
            {banners.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentIndex
                    ? 'bg-primary w-8'
                    : 'bg-muted-foreground/50 hover:bg-muted-foreground'
                }`}
                aria-label={`Go to banner ${index + 1}`}
              />
            ))}
          </div>
        </>
      )}
    </section>
  );
}
