import { useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

const ProgressChart = ({ data, metricLabel, empty }) => {
  const chartData = useMemo(() => {
    return (data || []).map((item, index) => ({
      ...item,
      label: item.label || `W${index + 1}`,
      value: Math.min(100, Math.max(0, Number(item.value) || 0)),
    }))
  }, [data])

  if (empty || chartData.length === 0) {
    return (
      <div className="flex h-[165px] min-h-[150px] max-h-[180px] items-center justify-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/50 px-6 text-center text-sm text-slate-400">
        No performance data yet. Complete this module to unlock performance trends.
      </div>
    )
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={metricLabel}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.2 }}
        className="h-[300px]"
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 6, right: 6, left: -10, bottom: 0 }}>
            <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" stroke="#64748b" tickLine={false} axisLine={false} fontSize={11} />
            <YAxis stroke="#64748b" tickLine={false} axisLine={false} domain={[0, 100]} fontSize={11} />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={2.5} dot={{ r: 2.5 }} activeDot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>
    </AnimatePresence>
  )
}

export default ProgressChart
