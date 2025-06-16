import React, { useEffect, useState } from 'react';
import axios from 'axios';
axios.defaults.withCredentials = true;
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';

// Columns for the table
const columns = [
  { id: 'Applied', label: 'Applied', minWidth: 170, align: 'center' },
  { id: 'Interviewing', label: 'Interviewing', minWidth: 170, align: 'center' },
  { id: 'Offer', label: 'Offer', minWidth: 170, align: 'center' }
];

// Global state updater (populated when component mounts)
let setters = {};

// Shared function to fetch counts
const fetchCounts = () => {
  const token = localStorage.getItem('token');
  const config = {
    headers: {
      Authorization: token,
    },
    withCredentials: true,
  };

  axios.get('http://localhost:8080/api/userApplicationData/count', config)
    .then((res) => setters.setApplicationCount?.(res.data.count))
    .catch((err) => console.error('Error fetching application count:', err));

  axios.get('http://localhost:8080/api/userApplicationData/interviewCount', config)
    .then((res) => setters.setInterviewCount?.(res.data.interviewCount))
    .catch((err) => console.error('Error fetching interview count:', err));

  axios.get('http://localhost:8080/api/userApplicationData/offerCount', config)
    .then((res) => setters.setOfferCount?.(res.data.offerCount))
    .catch((err) => console.error('Error fetching offer count:', err));
};

// ✅ Export for other components (like your form) to call it
export { fetchCounts };

export default function AutoTopBoard() {
  const [applicationCount, setApplicationCount] = useState(0);
  const [interviewCount, setInterviewCount] = useState(0);
  const [offerCount, setOfferCount] = useState(0);

  useEffect(() => {
    // Register setters to be used by fetchCounts()
    setters = {
      setApplicationCount,
      setInterviewCount,
      setOfferCount
    };

    // Fetch counts on component mount
    fetchCounts();
  }, []);

  return (
    <Paper sx={{ width: '80%', overflow: 'auto', margin: '0 auto', boxShadow: 3, borderRadius: 2 }}>
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader size="small" sx={{ minWidth: 500 }}>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  style={{
                    minWidth: column.minWidth,
                    fontWeight: 'bold',
                    background: 'black',
                    color: 'white'
                  }}
                >
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell align="center">
                <Typography variant="body1">{applicationCount}</Typography>
              </TableCell>
              <TableCell align="center">
                <Typography variant="body1">{interviewCount}</Typography>
              </TableCell>
              <TableCell align="center">
                <Typography variant="body1">{offerCount}</Typography>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
