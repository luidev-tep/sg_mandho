import React, { useRef, useEffect, useState } from 'react';
import { useThemeProvider } from '../utils/ThemeContext';

import { chartColors } from './ChartjsConfig';
import {
  Chart, BarController, BarElement, LinearScale, CategoryScale, Tooltip, Legend,
} from 'chart.js';

// Import utilities
import { formatValue } from '../utils/Utils';

Chart.register(BarController, BarElement, LinearScale, CategoryScale, Tooltip, Legend);

function BarChartFraction({
  data,
  width,
  height
}) {
  
  //console.log("BarChartFraction recibiendo data:", data);
  //console.log("BarChartFraction width/height:", width, height);

  const [chart, setChart] = useState(null)
  const canvas = useRef(null);
  const { currentTheme } = useThemeProvider();
  const darkMode = currentTheme === 'dark';
  const { textColor, gridColor, tooltipBodyColor, tooltipBgColor, tooltipBorderColor } = chartColors; 

  useEffect(() => {
    const ctx = canvas.current;
    // eslint-disable-next-line no-unused-vars
    const newChart = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        layout: {
          padding: {
            top: 12,
            bottom: 16,
            left: 20,
            right: 20,
          },
        },
        scales: {
          y: {
            border: {
              display: false,
            },
            beginAtZero: true,
            ticks: {
              maxTicksLimit: 5,
              callback: (value) => formatValue(value),
              color: darkMode ? textColor.dark : textColor.light,
            },
            grid: {
              color: darkMode ? gridColor.dark : gridColor.light,
            },
          },
          x: {
            type: 'category', // <-- CAMBIO PRINCIPAL: usar 'category' en lugar de 'time'
            border: {
              display: false,
            },
            grid: {
              display: false,
            },
            ticks: {
              maxRotation: 45, // <-- Permitir rotación para nombres largos de manzanas
              minRotation: 0,
              color: darkMode ? textColor.dark : textColor.light,
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              title: (context) => {
                // Mostrar el nombre de la manzana en el título del tooltip
                return context[0].label;
              },
              label: (context) => {
                return `Ingresos: ${formatValue(context.parsed.y)}`;
              },
            },
            bodyColor: darkMode ? tooltipBodyColor.dark : tooltipBodyColor.light,
            backgroundColor: darkMode ? tooltipBgColor.dark : tooltipBgColor.light,
            borderColor: darkMode ? tooltipBorderColor.dark : tooltipBorderColor.light,
          },
        },
        interaction: {
          intersect: false,
          mode: 'nearest',
        },
        animation: {
          duration: 200,
        },
        maintainAspectRatio: false,
        resizeDelay: 200,
        // Configuración adicional para barras
        elements: {
          bar: {
            borderRadius: 4,
            borderSkipped: 'bottom',
          }
        }
      },
    });
    setChart(newChart);
    return () => newChart.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]); // <-- IMPORTANTE: Incluir 'data' en las dependencias para que se actualice cuando cambien los datos

  useEffect(() => {
    if (!chart) return;

    if (darkMode) {
      chart.options.scales.x.ticks.color = textColor.dark;
      chart.options.scales.y.ticks.color = textColor.dark;
      chart.options.scales.y.grid.color = gridColor.dark;
      chart.options.plugins.tooltip.bodyColor = tooltipBodyColor.dark;
      chart.options.plugins.tooltip.backgroundColor = tooltipBgColor.dark;
      chart.options.plugins.tooltip.borderColor = tooltipBorderColor.dark;
    } else {
      chart.options.scales.x.ticks.color = textColor.light;
      chart.options.scales.y.ticks.color = textColor.light;
      chart.options.scales.y.grid.color = gridColor.light;
      chart.options.plugins.tooltip.bodyColor = tooltipBodyColor.light;
      chart.options.plugins.tooltip.backgroundColor = tooltipBgColor.light;
      chart.options.plugins.tooltip.borderColor = tooltipBorderColor.light;
    }
    chart.update('none');
  }, [currentTheme, chart]);

  // Actualizar datos del gráfico cuando cambien
  useEffect(() => {
    if (!chart) return;
    
    chart.data = data;
    chart.update('none');
  }, [data, chart]);

  return (
    <canvas ref={canvas} width={width} height={height}></canvas>
  );
}

export default BarChartFraction;

/*
PRINCIPALES CAMBIOS RESPECTO A BarChart02:

1. **Escala X**: Cambiado de 'time' a 'category' para manejar nombres en lugar de fechas
2. **Imports**: Cambiado TimeScale por CategoryScale
3. **Rotación de labels**: Permitida rotación hasta 45° para nombres largos de manzanas
4. **Tooltip**: Mejorado para mostrar mejor la información de manzanas
5. **Dependencias useEffect**: Agregado 'data' para actualizar cuando cambien los datos
6. **Actualización de datos**: Nuevo useEffect para actualizar el gráfico cuando cambien los datos

CONFIGURACIÓN ESPECÍFICA PARA MANZANAS:
- Escala categórica que acepta strings como labels
- Rotación de texto para nombres largos
- Tooltips optimizados para mostrar nombres de manzanas
- Actualización automática cuando cambien los datos de entrada
*/