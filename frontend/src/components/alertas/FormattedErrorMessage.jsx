// src/components/FormattedErrorMessage.jsx

import React from 'react';

/**

 * Parsea y formatea un mensaje de error de pagos pendientes.

 * Soporta dos formatos:

 * 1. Un formato simple en una sola línea.

 * 2. Un formato detallado y multilínea agrupado por año.

 * @param {object} props - Propiedades del componente.

 * @param {string} props.message - El mensaje de error a mostrar.

 */

const FormattedErrorMessage = ({ message }) => {

  const baseTitle = "El usuario aun tiene pagos pendientes";

  const fullTitleRegex = /El usuario aun tiene pagos pendientes[^:]*:/;



  if (typeof message !== 'string' || !message.trim().startsWith(baseTitle)) {

    return <>{message}</>; // No es el error esperado, muestra el mensaje original.

  }



  const paymentsByYear = {};



  // --- Lógica para el formato multilínea (formato nuevo) ---

  const lines = message.split('\n').filter(line => line.trim() !== '');

  if (lines.length > 1) {

    let currentYear = null;

    const yearRegex = /^\s*Año\s+(\d{4}):\s*$/;

    const serviceRegex = /^\s*Servicio de\s+(.+?)\s+-\s+Debe:\s+\$\s*([\d.]+)\s*$/;



    for (const line of lines) {

      const yearMatch = line.match(yearRegex);

      if (yearMatch) {

        currentYear = yearMatch[1];

        if (!paymentsByYear[currentYear]) {

          paymentsByYear[currentYear] = [];

        }

        continue;

      }



      const serviceMatch = line.match(serviceRegex);

      if (serviceMatch && currentYear) {

        paymentsByYear[currentYear].push({

          service: serviceMatch[1].trim(),

          amount: parseFloat(serviceMatch[2]),

        });

      }

    }

  }



  // --- Lógica para el formato de una sola línea (formato antiguo) ---

  if (Object.keys(paymentsByYear).length === 0) {

    const titleMatch = message.match(fullTitleRegex);

    if (titleMatch) {

      const titleText = titleMatch[0];

      const content = message.substring(titleText.length).trim();

      const yearRegex = /Año\s(\d{4}):\s(.*?)(?=\sAño\s\d{4}|$)/g;

      let match;



      while ((match = yearRegex.exec(content)) !== null) {

        const year = match[1];

        const serviceText = match[2].trim();

        if (!paymentsByYear[year]) {

          paymentsByYear[year] = [];

        }

        // Para este formato, el amount no está disponible, solo el texto.

        paymentsByYear[year].push({ service: serviceText, amount: null });

      }

    }

  }



  // --- Renderizado para el nuevo formato ---

  if (Object.keys(paymentsByYear).length > 0) {

    return (

      <div>

        <h4 className="font-semibold mb-2 text-gray-900 dark:text-white">El usuario tiene pagos pendientes:</h4>

        <div className="overflow-auto max-h-80 border border-red-300 dark:border-red-700 rounded-md bg-red-50/50 dark:bg-red-900/50 p-2 space-y-4">

          {Object.keys(paymentsByYear).sort().map(year => {

            const payments = paymentsByYear[year];

            if (payments.length === 0) return null;

            const yearTotal = payments.reduce((sum, p) => sum + (p.amount || 0), 0);

            const hasAmounts = payments.some(p => p.amount !== null);



            return (

              <div key={year} className="bg-red-100/50 dark:bg-red-900/30 rounded-lg">

                <h5 className="font-bold text-md p-2 bg-red-200/60 dark:bg-red-800/50 rounded-t-lg text-gray-900 dark:text-white">{`Año ${year}`}</h5>

                <table className="min-w-full text-sm text-left">

                  <tbody className="divide-y divide-red-200/50 dark:divide-red-800/50">

                    {payments.map((p, index) => (

                      <tr key={index}>

                        <td className="p-2 capitalize text-gray-900 dark:text-white">{p.service}</td>

                        {hasAmounts && (

                          <td className="p-2 text-right font-mono text-gray-900 dark:text-white">

                            {p.amount !== null ? `$${p.amount.toFixed(2)}` : ''}

                          </td>

                        )}

                      </tr>

                    ))}

                  </tbody>

                  {hasAmounts && yearTotal > 0 && (

                    <tfoot>

                      <tr className="border-t-2 border-red-300 dark:border-red-700">

                        <td className="p-2 font-bold text-right text-gray-900 dark:text-white">Total del Año:</td>

                        <td className="p-2 font-bold text-right font-mono text-gray-900 dark:text-white">{`$${yearTotal.toFixed(2)}`}</td>

                      </tr>

                    </tfoot>

                  )}

                </table>

              </div>

            );

          })}

        </div>

      </div>

    );

  }



  // Fallback final: si algo falla, muestra el mensaje original.

  return <>{message}</>;

};



export default FormattedErrorMessage;