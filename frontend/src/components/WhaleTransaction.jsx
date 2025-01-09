import React, { useState, useEffect } from 'react';

const WhaleTransaction = () => {
  const [transactionData, setTransactionData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/latest-transaction');
        const data = await response.json();
        if (data.error) {
          setError(data.error);
        } else {
          setTransactionData(data);
        }
      } catch (err) {
        setError('Failed to fetch data');
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (error) return <div>Error: {error}</div>;
  if (!transactionData) return <div>Loading...</div>;

  return (
    <div className="w-full max-w-4xl bg-gray-50 p-8 rounded-lg">
      {/* Transaction Type and Amount */}
      <div className="text-center mb-8">
        <div className="text-2xl text-black font-semibold mb-2">
          {transactionData.type}
        </div>
        <div className="flex justify-center items-center gap-4">
          <span className="text-xl text-gray-600">
            {transactionData.btc_amount} BTC
          </span>
          <span className="text-lg text-red-600">
            (${transactionData.usd_value} USD)
          </span>
        </div>
      </div>

      {/* Transaction Flow */}
      <div className="flex justify-between items-center mb-8">
        {/* From Box */}
        <div className="w-[300px] p-4 bg-white border-2 border-black rounded-lg">
          <div className="text-sm mb-1">From: {transactionData.from.address}</div>
          <div className="text-sm mb-2">({transactionData.from.label})</div>
          <div className="text-xs text-gray-600 space-y-1">
            <div className="font-mono">
              [<span className="text-green-500">↑</span>{transactionData.from.stats.sent_count}|<span className="text-red-500">↓</span>{transactionData.from.stats.received_count}]
            </div>
            <div className="font-mono">
               Total: <span className="text-green-500">↑</span>{transactionData.from.stats.total_sent.toFixed(2)}|<span className="text-red-500">↓</span>{transactionData.from.stats.total_received.toFixed(2)} BTC
            </div>
          </div>
        </div>

        {/* Arrow */}
         <div className="flex-grow flex justify-center">
          <svg className="w-24 h-8" viewBox="0 0 96 32">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7" 
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon
                  points="0 0, 10 3.5, 0 7"
                  fill="black"
                />
              </marker>
            </defs>
            <line
              x1="0"
              y1="16"
              x2="88"
              y2="16"
              stroke="black"
              strokeWidth="2"
              markerEnd="url(#arrowhead)"
            />
          </svg>
        </div>

        {/* To Box */}
        <div className="w-[300px] p-4 bg-white border-2 border-black rounded-lg">
          <div className="text-sm mb-1">To: {transactionData.to.address}</div>
          <div className="text-sm mb-2">({transactionData.to.label})</div>
            <div className="text-xs text-gray-600 space-y-1">
            <div className="font-mono">
              [<span className="text-green-500">↑</span>{transactionData.to.stats.sent_count}|<span className="text-red-500">↓</span>{transactionData.to.stats.received_count}]
            </div>
            <div className="font-mono">
              Total: <span className="text-green-500">↑</span>{transactionData.to.stats.total_sent.toFixed(2)}|<span className="text-red-500">↓</span>{transactionData.to.stats.total_received.toFixed(2)} BTC
            </div>
          </div>
        </div>
      </div>

      {/* Transaction Details */}
      <div className="text-center text-xs text-gray-600">
        <span>Hash: {transactionData.hash}</span>
        <span className="mx-2">|</span>
        <span className="text-red-600">
          Fee: {transactionData.fee.btc} BTC (${transactionData.fee.usd} USD)
        </span>
        <span className="mx-2">|</span>
        <span>{transactionData.timestamp}</span>
      </div>
    </div>
  );
};

export default WhaleTransaction;
