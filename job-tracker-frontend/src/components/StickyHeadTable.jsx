import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
axios.defaults.withCredentials = true;
import {
  Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TablePagination, TableRow, TextField, Select,
  MenuItem, IconButton, Typography
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import AddIcon from '@mui/icons-material/Add';
import { fetchCounts } from './AutoTopBoard'; 

const statusOptions = ['Applied', 'Interviewing', 'Rejected', 'Offer'];

export default function StickyHeadTable({ onUpdateCounts }) {
  const [rows, setRows] = useState([]);
  const [company, setCompany] = useState('');
  const [position, setPosition] = useState('');
  const [status, setStatus] = useState('');
  const [editingRowId, setEditingRowId] = useState(null);
  const [hoveredDelete, setHoveredDelete] = useState(null);
  const [hoveredAdd, setHoveredAdd] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const rowRefs = useRef({});

  const capitalizeFirstLetter = (str) =>
    str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();

  useEffect(() => {
    const token = localStorage.getItem('token');
    axios.get('http://localhost:8080/api/userApplicationData', {
  headers: {
    Authorization: token,
  },
  withCredentials: true,
})
      .then((res) => {
        const normalized = res.data.map((r) => ({
          ...r,
          status: capitalizeFirstLetter(r.status)
        }));
        setRows(normalized);
      })
      .catch((err) => console.error('Error fetching data:', err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
const res = await axios.post(
  'http://localhost:8080/api/userApplicationData',
  { company, position, status },
  {
    headers: { Authorization: token },
    withCredentials: true
  }
);
      setRows([...rows, { id: res.data.id, company, position, status }]);
    setCompany('');
    setPosition('');
    setStatus('');

    // 👇 Trigger dashboard to update counts
    if (onUpdateCounts) onUpdateCounts();


  } catch (err) {
    console.error('Error submitting form:', err);
  }
};

  const handleDelete = async (id) => {
    try {
      const token = localStorage.getItem('token');
await axios.delete(
  `http://localhost:8080/api/userApplicationData/${id}`,
  {
    headers: { Authorization: token },
    withCredentials: true
  }
);
      setRows(rows.filter((r) => r.id !== id));
      if (onUpdateCounts) onUpdateCounts();
    } catch (err) {
      console.error('Error deleting row:', err);
    }
  };

  const handleCellChange = async (index, key, value) => {
    const updated = [...rows];
    updated[index][key] = value;
    setRows(updated);
    try {
      const token = localStorage.getItem('token');
await axios.put(
  `http://localhost:8080/api/userApplicationData/${updated[index].id}`,
  updated[index],
  {
    headers: { Authorization: token },
    withCredentials: true
  }
);
      if (onUpdateCounts) onUpdateCounts();
    } catch (err) {
      console.error('Error saving edit:', err);
    }
  };

  const handleRowBlur = (rowId) => {
    setTimeout(() => {
      const active = document.activeElement;
  
      // If the active element is part of a dropdown menu (Select uses a popper),
      // ignore the blur event
      const isDropdown = document.querySelector('[role="listbox"]')?.contains(active);
      const rowEl = rowRefs.current[rowId];
  
      if (!isDropdown && rowEl && !rowEl.contains(active)) {
        setEditingRowId(null);
      }
    }, 0); // 0ms delay is enough — ensures focus settles
  };
  

  return (
    <Paper sx={{ width: '80%', margin: '0 auto', boxShadow: 3, borderRadius: 2 }}>
      <form onSubmit={handleSubmit}>
        <TableContainer>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell align="center">Company</TableCell>
                <TableCell align="center">Position</TableCell>
                <TableCell align="center">Status</TableCell>
                <TableCell align="center" />
              </TableRow>
            </TableHead>
            <TableBody>
              {rows
                .sort((a, b) => (a.company === "Unknown" ? -1 : b.company === "Unknown" ? 1 : 0))
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row, index) => {
                  const isEditing = editingRowId === row.id;
                  return (
                    <TableRow
                      key={row.id}
                      ref={(el) => rowRefs.current[row.id] = el}
                      tabIndex={-1}
                      onClick={() => setEditingRowId(row.id)}
                      onBlur={() => handleRowBlur(row.id)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell align="center">
                        {isEditing ? (
                          <TextField
                            variant="standard"
                            value={row.company}
                            onChange={(e) => handleCellChange(index, 'company', e.target.value)}
                            fullWidth
                            autoFocus
                          />
                        ) : (
                          <Typography>{row.company}</Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        {isEditing ? (
                          <TextField
                            variant="standard"
                            value={row.position}
                            onChange={(e) => handleCellChange(index, 'position', e.target.value)}
                            fullWidth
                          />
                        ) : (
                          <Typography>{row.position}</Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        {isEditing ? (
                          <Select
                            value={row.status}
                            onChange={(e) => handleCellChange(index, 'status', e.target.value)}
                            variant="standard"
                            fullWidth
                          >
                            {statusOptions.map((s) => (
                              <MenuItem key={s} value={s}>{s}</MenuItem>
                            ))}
                          </Select>
                        ) : (
                          <Typography>{row.status}</Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          onMouseEnter={() => setHoveredDelete(row.id)}
                          onMouseLeave={() => setHoveredDelete(null)}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(row.id);
                          }}
                        >
                          {hoveredDelete === row.id ? (
                            <DeleteIcon color="primary" />
                          ) : (
                            <DeleteOutlinedIcon />
                          )}
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              <TableRow>
                <TableCell align="center">
                  <TextField
                    variant="standard"
                    fullWidth
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="Enter company"
                  />
                </TableCell>
                <TableCell align="center">
                  <TextField
                    variant="standard"
                    fullWidth
                    value={position}
                    onChange={(e) => setPosition(e.target.value)}
                    placeholder="Enter position"
                  />
                </TableCell>
                <TableCell align="center">
                  <Select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    fullWidth
                    variant="standard"
                    displayEmpty
                  >
                    <MenuItem value="" disabled>Select status</MenuItem>
                    {statusOptions.map((s) => (
                      <MenuItem key={s} value={s}>{s}</MenuItem>
                    ))}
                  </Select>
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    type="submit"
                    onMouseEnter={() => setHoveredAdd(true)}
                    onMouseLeave={() => setHoveredAdd(false)}
                  >
                    <AddIcon color={hoveredAdd ? 'primary' : 'inherit'} />
                  </IconButton>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </form>
      <TablePagination
        rowsPerPageOptions={[10, 25, 100]}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={(e, newPage) => setPage(newPage)}
        onRowsPerPageChange={(e) =>
          setRowsPerPage(parseInt(e.target.value, 10))
        }
      />
    </Paper>
  );
}
