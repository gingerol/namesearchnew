import { useRef, useEffect } from 'react';
import { cn } from '../../../lib/utils';
import { Line } from 'react-chartjs-2';
import type {
  ChartData,
  ChartOptions,
  ChartDataset,
} from 'chart.js';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

type TrendChartProps = {
  data: ChartData<'line'>;
  title?: string;
  className?: string;
  height?: number | string;
  width?: number | string;
  options?: ChartOptions<'line'>;
};

export const TrendChart = ({
  data,
  title,
  className,
  height = 300,
  width = '100%',
  options: customOptions,
}: TrendChartProps) => {
  const chartRef = useRef<any>(null);

  // Default options
  const defaultOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          boxWidth: 12,
          padding: 16,
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 14,
          weight: 500,
        },
        padding: {
          bottom: 16,
        },
      },
      tooltip: {
        enabled: true,
        intersect: false,
        backgroundColor: 'white',
        titleColor: '#1F2937',
        titleFont: {
          weight: 500,
          size: 12,
        },
        bodyColor: '#4B5563',
        bodyFont: {
          weight: 400,
          size: 12,
        },
        borderColor: '#E5E7EB',
        borderWidth: 1,
        displayColors: true,
        usePointStyle: true,
        padding: 12,
        cornerRadius: 6,
        callbacks: {
          label: function (context) {
            let label = context.dataset.label || '';
            if (label) label += ': ';
            if (context.parsed.y !== null) {
              label += new Intl.NumberFormat('en-US').format(context.parsed.y);
            }
            return label;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 12,
          },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          drawOnChartArea: true,
          drawTicks: false,
        },
        ticks: {
          font: {
            size: 12,
          },
          callback: function (value) {
            return new Intl.NumberFormat('en-US', {
              notation: 'compact',
              compactDisplay: 'short',
            }).format(Number(value));
          },
        },
      },
    },
    elements: {
      line: {
        tension: 0.3,
        borderWidth: 2,
        fill: true,
      },
      point: {
        radius: 0,
        hoverRadius: 6,
        hoverBorderWidth: 2,
      },
    },
    interaction: {
      mode: 'index',
      intersect: false,
    },
  };

  const options = {
    ...defaultOptions,
    ...customOptions,
  };

  // Handle window resize for responsive charts
  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current) {
        chartRef.current.update();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Apply gradient background
  const chartData = {
    ...data,
    datasets: data.datasets.map(dataset => ({
      ...dataset,
      backgroundColor: (context: any) => {
        const chart = context.chart;
        const { ctx, chartArea } = chart;
        
        if (!chartArea) return null;
        
        const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
        gradient.addColorStop(0, `${dataset.borderColor}33`);
        gradient.addColorStop(1, `${dataset.borderColor}00`);
        return gradient;
      },
    })),
  };

  return (
    <div className={cn('relative', className)} style={{ height, width }}>
      <Line ref={chartRef} data={chartData} options={options} />
    </div>
  );
};

// Helper function to generate sample data
export const generateSampleData = (count = 7, datasetsCount = 1): ChartData<'line'> => {
  const labels = [];
  const now = new Date();
  
  for (let i = count - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
  }

  const colors = [
    { border: '#3B82F6', background: '#93C5FD' }, // blue
    { border: '#10B981', background: '#6EE7B7' }, // green
    { border: '#8B5CF6', background: '#C4B5FD' }, // purple
    { border: '#F59E0B', background: '#FCD34D' }, // amber
  ];

  const chartDatasets: ChartDataset<'line', number[]>[] = [];
  
  for (let i = 0; i < datasetsCount; i++) {
    const color = colors[i % colors.length];
    const data = [];
    let lastValue = 100 + Math.random() * 200;
    
    for (let j = 0; j < count; j++) {
      lastValue = Math.max(10, lastValue + (Math.random() - 0.4) * 30);
      data.push(Math.round(lastValue));
    }
    
    chartDatasets.push({
      label: `Dataset ${i + 1}`,
      data,
      borderColor: color.border,
      backgroundColor: color.background,
      tension: 0.3,
      fill: true,
    });
  }

  return { 
    labels, 
    datasets: chartDatasets 
  };
};
