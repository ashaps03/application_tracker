import React, { useState } from 'react';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

const columns = [
  { id: 'Applied', label: 'Applied', minWidth: 170, align: 'center' },
  { id: 'Interviewing', label: 'Interviewing', minWidth: 170, align: 'center' },
  { id: 'Offer', label: 'Offer', minWidth: 170, align: 'center' }
];

function createData(Applied, Interviewing, Offer) {
  return { Applied, Interviewing, Offer };
}

// Mock row
const rows = [createData('4', '2', '0')];

export default function AutoTopBoard() {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

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
            {rows
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((row, idx) => (
                <TableRow hover tabIndex={-1} key={idx}>
                  {columns.map((column) => {
                    const value = row[column.id];
                    return (
                      <TableCell key={column.id} align={column.align || 'left'}>
                        {value}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
