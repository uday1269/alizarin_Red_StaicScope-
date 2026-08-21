package com.simats.stainscope.ui.history

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.outlined.CompareArrows
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.simats.stainscope.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    onNavigateToDashboard: () -> Unit,
    onNavigateToAnalysis: () -> Unit,
    onNavigateToCompare: () -> Unit,
    onNavigateToReports: () -> Unit,
    onNavigateToProfile: () -> Unit,
    onNavigateBack: () -> Unit,
    onNavigateToResults: (String) -> Unit,
    viewModel: HistoryViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var visible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        visible = true
        viewModel.loadHistory()
    }

    Scaffold(
        topBar = {
            Column(modifier = Modifier.background(Color.White)) {
                TopAppBar(
                    title = { 
                        Text(
                            "Reports Repository", 
                            fontWeight = FontWeight.Black, 
                            fontSize = 22.sp,
                            color = Color.Black
                        ) 
                    },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Color.Black)
                        }
                    },
                    actions = {
                        IconButton(onClick = { }) {
                            Icon(Icons.Outlined.Notifications, contentDescription = "Notifications", tint = Color.Black)
                        }
                        IconButton(onClick = onNavigateToProfile) {
                            Surface(
                                shape = CircleShape,
                                color = PrimaryMaroon.copy(alpha = 0.1f),
                                modifier = Modifier.size(38.dp)
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Text("SC", color = PrimaryMaroon, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                                }
                            }
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White)
                )

                ScrollableTabRow(
                    selectedTabIndex = 3,
                    containerColor = Color.White,
                    contentColor = PrimaryMaroon,
                    edgePadding = 16.dp,
                    divider = {},
                    indicator = { tabPositions ->
                        if (tabPositions.isNotEmpty()) {
                            TabRowDefaults.SecondaryIndicator(
                                Modifier.tabIndicatorOffset(tabPositions[3]),
                                color = PrimaryMaroon,
                                height = 3.dp
                            )
                        }
                    }
                ) {
                    val tabs = listOf(
                        "Home" to Icons.Outlined.Dashboard,
                        "Upload & Analyze" to Icons.Outlined.CloudUpload,
                        "Compare" to Icons.AutoMirrored.Outlined.CompareArrows,
                        "Reports" to Icons.Outlined.Description
                    )
                    tabs.forEachIndexed { index, pair ->
                        Tab(
                            selected = index == 3,
                            onClick = { 
                                when(index) {
                                    0 -> onNavigateToDashboard()
                                    1 -> onNavigateToAnalysis()
                                    2 -> onNavigateToCompare()
                                    3 -> {}
                                }
                            },
                            text = { 
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.padding(vertical = 12.dp)
                                ) {
                                    Icon(
                                        imageVector = pair.second,
                                        contentDescription = null,
                                        modifier = Modifier.size(16.dp),
                                        tint = if (index == 3) PrimaryMaroon else TextGray
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = pair.first, 
                                        fontWeight = if (index == 3) FontWeight.Bold else FontWeight.Medium,
                                        fontSize = 13.sp,
                                        color = if (index == 3) PrimaryMaroon else TextGray
                                    )
                                }
                            }
                        )
                    }
                }
                HorizontalDivider(color = Color(0xFFF0F0F0))
            }
        }
    ) { padding ->
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600)) + slideInVertically(initialOffsetY = { 60 })
        ) {
            PullToRefreshBox(
                isRefreshing = uiState.isRefreshing,
                onRefresh = { viewModel.loadHistory(isRefresh = true) },
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color(0xFFFAFAFA))
                ) {
                    // Search Bar
                    Surface(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(20.dp),
                        shape = RoundedCornerShape(16.dp),
                        color = Color.White,
                        shadowElevation = 2.dp,
                        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
                    ) {
                        OutlinedTextField(
                            value = uiState.searchQuery,
                            onValueChange = viewModel::onSearchQueryChange,
                            modifier = Modifier.fillMaxWidth(),
                            placeholder = { Text("Search by ID, Cell Line, or Date...", fontSize = 14.sp, color = TextGray) },
                            leadingIcon = { Icon(Icons.Outlined.Search, contentDescription = null, tint = PrimaryMaroon) },
                            trailingIcon = { 
                                if (uiState.searchQuery.isNotEmpty()) {
                                    IconButton(onClick = { viewModel.onSearchQueryChange("") }) {
                                        Icon(Icons.Default.Close, contentDescription = "Clear", tint = TextGray)
                                    }
                                }
                            },
                            shape = RoundedCornerShape(16.dp),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = Color.Transparent,
                                unfocusedBorderColor = Color.Transparent,
                                focusedContainerColor = Color.Transparent,
                                unfocusedContainerColor = Color.Transparent,
                                cursorColor = PrimaryMaroon
                            ),
                            singleLine = true
                        )
                }

                // Filter Chips
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    HistoryFilterChip("All Scans", true)
                    HistoryFilterChip("High Mineralized", false)
                    HistoryFilterChip("Pinned", false)
                }

                Spacer(modifier = Modifier.height(10.dp))

                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(20.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    items(uiState.analyses) { item ->
                        HistoryListItem(
                            item = item,
                            onOpen = { onNavigateToResults(item.id) },
                            onDelete = { viewModel.deleteAnalysis(item.id) },
                            onTogglePin = { viewModel.togglePin(item.id) }
                        )
                    }
                    
                    item {
                        Spacer(modifier = Modifier.height(40.dp))
                    }
                }
            }
        }
    }
}
}

@Composable
fun HistoryFilterChip(label: String, isSelected: Boolean) {
    Surface(
        modifier = Modifier.clickable { },
        shape = RoundedCornerShape(10.dp),
        color = if (isSelected) PrimaryMaroon else Color.White,
        border = BorderStroke(1.dp, if (isSelected) PrimaryMaroon else Color(0xFFEEEEEE))
    ) {
        Text(
            text = label,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = if (isSelected) Color.White else TextGray,
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp)
        )
    }
}

@Composable
fun HistoryListItem(
    item: HistoryItem,
    onOpen: () -> Unit,
    onDelete: () -> Unit,
    onTogglePin: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
            .shadow(2.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        modifier = Modifier.size(44.dp),
                        shape = RoundedCornerShape(12.dp),
                        color = PrimaryMaroon.copy(alpha = 0.05f)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.Biotech, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(22.dp))
                        }
                    }
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(item.sampleName, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Black, maxLines = 1)
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("ID: ${item.id}", fontSize = 12.sp, color = PrimaryMaroon, fontWeight = FontWeight.Black)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("•", fontSize = 12.sp, color = TextGray)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(item.date, fontSize = 12.sp, color = TextGray)
                        }
                    }
                }
                
                IconButton(
                    onClick = onTogglePin, 
                    modifier = Modifier.size(24.dp)
                ) {
                    Icon(
                        imageVector = if (item.isPinned) Icons.Default.PushPin else Icons.Outlined.PushPin,
                        contentDescription = "Pin",
                        tint = if (item.isPinned) PrimaryMaroon else TextGray.copy(alpha = 0.3f),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row {
                    HistoryStat("MINERAL AREA", item.mineralArea, SuccessGreen)
                    Spacer(modifier = Modifier.width(24.dp))
                    HistoryStat("STAIN INTENSITY", item.stainIntensity, PrimaryMaroon)
                }
                
                Surface(
                    color = if (item.status.contains("High")) SuccessGreen.copy(0.1f) else Color(0xFFFFF3E0),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .background(if (item.status.contains("High")) SuccessGreen else Color(0xFFF57C00), CircleShape)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = item.status.uppercase(),
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Black,
                            color = if (item.status.contains("High")) SuccessGreen else Color(0xFFF57C00),
                            letterSpacing = 0.5.sp
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            HorizontalDivider(color = Color(0xFFF5F5F5))
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Button(
                    onClick = onOpen,
                    modifier = Modifier.weight(1f).height(44.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryMaroon)
                ) {
                    Icon(Icons.Default.Visibility, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("View Report", fontSize = 13.sp, fontWeight = FontWeight.Bold)
                }
                Spacer(modifier = Modifier.width(12.dp))
                OutlinedButton(
                    onClick = onDelete,
                    modifier = Modifier.size(44.dp),
                    shape = RoundedCornerShape(12.dp),
                    border = BorderStroke(1.dp, Color(0xFFEEEEEE)),
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Icon(Icons.Default.DeleteOutline, contentDescription = "Delete", tint = Color(0xFFD32F2F), modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}

@Composable
fun HistoryStat(label: String, value: String, valueColor: Color) {
    Column {
        Text(label, fontSize = 9.sp, fontWeight = FontWeight.Bold, color = TextGray, letterSpacing = 0.5.sp)
        Text(value, fontSize = 16.sp, fontWeight = FontWeight.Black, color = valueColor)
    }
}
