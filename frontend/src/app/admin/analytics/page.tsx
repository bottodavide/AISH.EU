/**
 * Admin Analytics Dashboard
 * Descrizione: Dashboard analytics e metriche
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import { TrendingUp, Users, Eye, ShoppingCart, DollarSign, ArrowUp, ArrowDown } from 'lucide-react';

interface AnalyticsStats {
  pageviews: number;
  unique_visitors: number;
  total_sessions: number;
  avg_session_duration: number;
  bounce_rate: number;
  conversion_rate: number;
  total_revenue: number;
  total_orders: number;
}

interface TopPage {
  path: string;
  title: string;
  pageviews: number;
  unique_visitors: number;
  avg_time: number;
}

interface TrafficSource {
  source: string;
  visitors: number;
  percentage: number;
}

interface TimeSeriesData {
  date: string;
  pageviews: number;
  visitors: number;
  revenue: number;
}

type TimeRange = 'today' | 'week' | 'month' | 'year';

export default function AdminAnalyticsPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [topPages, setTopPages] = useState<TopPage[]>([]);
  const [trafficSources, setTrafficSources] = useState<TrafficSource[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('week');

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadAnalytics();
    }
  }, [isAuthenticated, isAdmin, timeRange]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Load all analytics data in parallel
      await Promise.all([
        loadStats(),
        loadTopPages(),
        loadTrafficSources(),
        loadTimeSeries(),
      ]);
    } catch (err) {
      setError(getErrorMessage(err));
      // Set mock data for development if endpoint doesn't exist
      setMockData();
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiClient.get<AnalyticsStats>(
        `/analytics/stats?range=${timeRange}`
      );
      setStats(response);
    } catch (err) {
      console.error('Failed to load analytics stats:', err);
      throw err;
    }
  };

  const loadTopPages = async () => {
    try {
      const response = await apiClient.get<TopPage[]>(
        `/analytics/top-pages?range=${timeRange}&limit=10`
      );
      setTopPages(response);
    } catch (err) {
      console.error('Failed to load top pages:', err);
    }
  };

  const loadTrafficSources = async () => {
    try {
      const response = await apiClient.get<TrafficSource[]>(
        `/analytics/traffic-sources?range=${timeRange}`
      );
      setTrafficSources(response);
    } catch (err) {
      console.error('Failed to load traffic sources:', err);
    }
  };

  const loadTimeSeries = async () => {
    try {
      const response = await apiClient.get<TimeSeriesData[]>(
        `/analytics/time-series?range=${timeRange}`
      );
      setTimeSeriesData(response);
    } catch (err) {
      console.error('Failed to load time series:', err);
    }
  };

  const setMockData = () => {
    // Mock data for development/testing
    setStats({
      pageviews: 12543,
      unique_visitors: 3421,
      total_sessions: 4892,
      avg_session_duration: 245,
      bounce_rate: 42.3,
      conversion_rate: 3.8,
      total_revenue: 18750,
      total_orders: 87,
    });

    setTopPages([
      { path: '/', title: 'Homepage', pageviews: 3421, unique_visitors: 2134, avg_time: 156 },
      { path: '/servizi', title: 'Servizi', pageviews: 2198, unique_visitors: 1543, avg_time: 234 },
      { path: '/blog', title: 'Blog', pageviews: 1876, unique_visitors: 1234, avg_time: 312 },
      { path: '/contatti', title: 'Contatti', pageviews: 987, unique_visitors: 876, avg_time: 98 },
      { path: '/chi-siamo', title: 'Chi Siamo', pageviews: 765, unique_visitors: 654, avg_time: 187 },
    ]);

    setTrafficSources([
      { source: 'Google Search', visitors: 1876, percentage: 54.8 },
      { source: 'Direct', visitors: 892, percentage: 26.1 },
      { source: 'Social Media', visitors: 421, percentage: 12.3 },
      { source: 'Referral', visitors: 232, percentage: 6.8 },
    ]);
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('it-IT').format(num);
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  const getChangeIndicator = (isPositive: boolean, value: number) => {
    const Icon = isPositive ? ArrowUp : ArrowDown;
    const colorClass = isPositive ? 'text-green-600' : 'text-red-600';

    return (
      <div className={`flex items-center gap-1 text-sm ${colorClass}`}>
        <Icon className="h-3 w-3" />
        <span>{formatPercentage(value)}</span>
      </div>
    );
  };

  if (authLoading || !isAuthenticated || !isAdmin) {
    return (
      <div className="container py-12">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p className="text-muted-foreground">Caricamento...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Analisi traffico, conversioni e comportamento utenti
          </p>
        </div>
        <Link href="/admin">
          <Button variant="outline">← Dashboard</Button>
        </Link>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>
            {error}
            <p className="mt-2 text-sm">
              Visualizzando dati di esempio. Gli endpoint analytics potrebbero non essere ancora implementati.
            </p>
          </AlertDescription>
        </Alert>
      )}

      {/* Time Range Filter */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Periodo di Analisi</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Button
              variant={timeRange === 'today' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTimeRange('today')}
            >
              Oggi
            </Button>
            <Button
              variant={timeRange === 'week' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTimeRange('week')}
            >
              Ultima Settimana
            </Button>
            <Button
              variant={timeRange === 'month' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTimeRange('month')}
            >
              Ultimo Mese
            </Button>
            <Button
              variant={timeRange === 'year' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTimeRange('year')}
            >
              Ultimo Anno
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Caricamento analytics...</p>
        </div>
      )}

      {/* Main Stats */}
      {!isLoading && stats && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Visualizzazioni
                  </CardTitle>
                  <Eye className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{formatNumber(stats.pageviews)}</div>
                {/* Mock trend indicator */}
                {getChangeIndicator(true, 12.5)}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Visitatori Unici
                  </CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{formatNumber(stats.unique_visitors)}</div>
                {getChangeIndicator(true, 8.3)}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Tasso Conversione
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{formatPercentage(stats.conversion_rate)}</div>
                {getChangeIndicator(true, 3.2)}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Fatturato
                  </CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{formatCurrency(stats.total_revenue)}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {stats.total_orders} ordini
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Secondary Metrics */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Sessioni Totali
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatNumber(stats.total_sessions)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Durata Media Sessione
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatDuration(stats.avg_session_duration)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Bounce Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatPercentage(stats.bounce_rate)}</div>
              </CardContent>
            </Card>
          </div>

          {/* Top Pages & Traffic Sources */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Top Pages */}
            <Card>
              <CardHeader>
                <CardTitle>Pagine Più Visitate</CardTitle>
                <CardDescription>
                  Le 5 pagine con più traffico nel periodo selezionato
                </CardDescription>
              </CardHeader>
              <CardContent>
                {topPages.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4">
                    Nessun dato disponibile
                  </p>
                ) : (
                  <div className="space-y-4">
                    {topPages.slice(0, 5).map((page, index) => (
                      <div
                        key={page.path}
                        className="flex items-center justify-between p-3 border rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-muted-foreground">
                              #{index + 1}
                            </span>
                            <div>
                              <div className="font-medium">{page.title}</div>
                              <div className="text-sm text-muted-foreground">{page.path}</div>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold">{formatNumber(page.pageviews)}</div>
                          <div className="text-sm text-muted-foreground">
                            {formatNumber(page.unique_visitors)} unici
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Traffic Sources */}
            <Card>
              <CardHeader>
                <CardTitle>Sorgenti di Traffico</CardTitle>
                <CardDescription>
                  Da dove provengono i tuoi visitatori
                </CardDescription>
              </CardHeader>
              <CardContent>
                {trafficSources.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4">
                    Nessun dato disponibile
                  </p>
                ) : (
                  <div className="space-y-4">
                    {trafficSources.map((source) => (
                      <div key={source.source} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{source.source}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-muted-foreground">
                              {formatNumber(source.visitors)} visitatori
                            </span>
                            <span className="font-semibold">
                              {formatPercentage(source.percentage)}
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className="bg-primary rounded-full h-2 transition-all"
                            style={{ width: `${source.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Chart Placeholder */}
          <Card>
            <CardHeader>
              <CardTitle>Andamento Temporale</CardTitle>
              <CardDescription>
                Visualizzazione grafica delle metriche nel tempo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center border-2 border-dashed rounded-lg">
                <div className="text-center text-muted-foreground">
                  <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="font-medium">Grafico in arrivo</p>
                  <p className="text-sm mt-2">
                    Integrazione con libreria charting (Chart.js, Recharts, ecc.)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
