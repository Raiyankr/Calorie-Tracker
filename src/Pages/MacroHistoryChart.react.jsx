import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const MacroHistoryChart = ({ token }) => {

  // const local = 'http://localhost:5055/api/user-history'
  const prod = 'https://calorie-tracker-xr.up.railway.app/api/user-history'

  const [data, setData] = useState([]);
  useEffect(() => {
    // Load saved macros on initial load
    fetch(prod, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    })
      .then(res => res.json())
      .then(data => {
        if (!data.error) {
            setData(data)
        }})
      .catch(err => {
        console.error('Failed to fetch history', err);
    });
  }, [token]);


  return (
    <div style={{ width: '100%', height: '100%' }} className="w-full h-96 container">
      <ResponsiveContainer>
        <LineChart  data={data}>
          <XAxis dataKey="date"/>
          <YAxis/>
          <Tooltip />
          <Legend />

          <Line type="monotone" dataKey="calorie" stroke="#6EEB7B" s/>
          <Line type="monotone" dataKey="protein" stroke="#E1647D" />
          <Line type="monotone" dataKey="carbs" stroke="#5678DF" />
          <Line type="monotone" dataKey="fat" stroke="#E98366" />
        </LineChart>
      </ResponsiveContainer>        
    </div>
  );
};

export default MacroHistoryChart;
