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
  const title = "El usuario aun tiene pagos pendientes:";

  if (typeof message !== 'string' || !message.trim().startsWith(title)) {
    return <>{message}</>; // No es el error esperado, muestra el mensaje original.
  }

  // --- Lógica para el nuevo formato multilínea ---
  const lines = message.split('\n');
  const paymentsByYear = {};
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

  // --- Lógica para el formato antiguo (si el parser multilínea no encontró nada) ---
  if (Object.keys(paymentsByYear).length === 0) {
    const paymentsString = message.substring(title.length).trim();
    const paymentItems = paymentsString.split('Año ').filter(item => item.trim());
    if (paymentItems.length > 0) {
        return (
            <div>
                <h4 className="font-semibold mb-2">{title}</h4>
                <div className="overflow-auto max-h-60 border border-red-300 dark:border-red-700 rounded-md bg-white/50 dark:bg-black/20">
                    <table className="min-w-full text-sm text-left">
                        <thead className="bg-red-200 dark:bg-red-800/50">
                            <tr><th className="p-2 font-semibold" colSpan="3">Pagos Detectados</th></tr>
                        </thead>
                        <tbody>
                            {paymentItems.map((item, index) => <tr key={index}><td className="p-2">{`Año ${item.trim()}`}</td></tr>)}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }
  }

  // --- Renderizado para el nuevo formato ---
  if (Object.keys(paymentsByYear).length > 0) {
    return (
      <div>
        <h4 className="font-semibold mb-2">{title}</h4>
        <div className="overflow-auto max-h-80 border border-red-300 dark:border-red-700 rounded-md bg-white/50 dark:bg-black/20 p-2 space-y-4">
          {Object.keys(paymentsByYear).sort().map(year => {
            const payments = paymentsByYear[year];
            if (payments.length === 0) return null;
            const yearTotal = payments.reduce((sum, p) => sum + p.amount, 0);

            return (
              <div key={year} className="bg-red-50/50 dark:bg-red-900/20 rounded-lg">
                <h5 className="font-bold text-md p-2 bg-red-200/60 dark:bg-red-800/50 rounded-t-lg">{`Año ${year}`}</h5>
                <table className="min-w-full text-sm text-left">
                  <tbody className="divide-y divide-red-200/50 dark:divide-red-800/50">
                    {payments.map((p, index) => (
                      <tr key={index}>
                        <td className="p-2 capitalize">{p.service}</td>
                        <td className="p-2 text-right font-mono">{`$${p.amount.toFixed(2)}`}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="border-t-2 border-red-300 dark:border-red-700">
                      <td className="p-2 font-bold text-right">Total del Año:</td>
                      <td className="p-2 font-bold text-right font-mono">{`$${yearTotal.toFixed(2)}`}</td>
                    </tr>
                  </tfoot>
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