import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

const generateMockData = () => {
  const data = [];
  let probability = 50;
  
  for (let i = 0; i <= 40; i++) {
    const variance = (Math.random() - 0.5) * 10;
    probability = Math.max(10, Math.min(90, probability + variance));
    data.push({
      move: i,
      probability: probability
    });
  }
  return data;
};

export const WinProbabilityChart = () => {
  const data = generateMockData();

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="move" 
            stroke="hsl(var(--muted-foreground))"
            label={{ value: 'Move Number', position: 'insideBottom', offset: -5, fill: 'hsl(var(--muted-foreground))' }}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            label={{ value: 'Win Probability (%)', angle: -90, position: 'insideLeft', fill: 'hsl(var(--muted-foreground))' }}
            domain={[0, 100]}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'hsl(var(--card))', 
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px',
              color: 'hsl(var(--foreground))'
            }}
            formatter={(value: number) => [`${value.toFixed(1)}%`, 'Win Probability']}
          />
          <ReferenceLine y={50} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
          <Line 
            type="monotone" 
            dataKey="probability" 
            stroke="hsl(var(--accent))" 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
