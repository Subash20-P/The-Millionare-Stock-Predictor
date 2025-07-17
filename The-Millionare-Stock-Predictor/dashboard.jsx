// D:/DIVINE_GENERAL/dashboard.jsx

import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableCell, TableBody } from "@/components/ui/table";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const Dashboard = () => {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    fetch("/DIVINE_GENERAL/trade_log.csv")
      .then((res) => res.text())
      .then((data) => {
        const rows = data.split("\n").slice(1);
        const parsed = rows
          .filter((r) => r)
          .map((r) => {
            const [time, symbol, action, price, predicted] = r.split(",");
            return { time, symbol, action, price: +price, predicted: +predicted };
          });
        setTrades(parsed);
      });
  }, []);

  return (
    <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card className="col-span-1">
        <CardContent>
          <h2 className="text-xl font-bold mb-2">📊 Trade History</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell>Time</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Predicted</TableCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {trades.slice(-10).reverse().map((t, i) => (
                <TableRow key={i}>
                  <TableCell>{t.time}</TableCell>
                  <TableCell>{t.action}</TableCell>
                  <TableCell>{t.price.toFixed(5)}</TableCell>
                  <TableCell>{t.predicted.toFixed(5)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card className="col-span-1">
        <CardContent>
          <h2 className="text-xl font-bold mb-2">📈 Performance Chart</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={trades.slice(-20)}>
              <XAxis dataKey="time" hide={true} />
              <YAxis domain={["auto", "auto"]} />
              <Tooltip />
              <Bar dataKey="price" fill="#4ade80" name="Executed Price" />
              <Bar dataKey="predicted" fill="#60a5fa" name="Predicted Price" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
