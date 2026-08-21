package com.simats.stainscope.ui.results

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.outlined.CompareArrows
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
import com.simats.stainscope.ui.theme.*

import androidx.compose.material3.pulltorefresh.PullToRefreshBox

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultsScreen(
    onNavigateToDashboard: () -> Unit,
    onNavigateToAnalysis: () -> Unit,
    onNavigateToCompare: () -> Unit,
    onNavigateToReports: () -> Unit,
    onNavigateToProfile: () -> Unit,
    onNavigateBack: () -> Unit,
    onCompareSample: () -> Unit,
    viewModel: ResultsViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var visible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        visible = true
    }

    Scaffold(
        topBar = {
            Column(modifier = Modifier.background(Color.White)) {
                TopAppBar(
                    title = { 
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "Results", 
                                fontWeight = FontWeight.Black, 
                                fontSize = 22.sp,
                                color = Color.Black
                            ) 
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack, 
                                contentDescription = "Back",
                                tint = Color.Black
                            )
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
                    selectedTabIndex = 1,
                    containerColor = Color.White,
                    contentColor = PrimaryMaroon,
                    edgePadding = 16.dp,
                    divider = {},
                    indicator = { tabPositions ->
                        if (tabPositions.isNotEmpty()) {
                            TabRowDefaults.SecondaryIndicator(
                                Modifier.tabIndicatorOffset(tabPositions[1]),
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
                            selected = index == 1,
                            onClick = { 
                                when(index) {
                                    0 -> onNavigateToDashboard()
                                    1 -> onNavigateToAnalysis()
                                    2 -> onNavigateToCompare()
                                    3 -> onNavigateToReports()
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
                                        tint = if (index == 1) PrimaryMaroon else TextGray
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = pair.first, 
                                        fontWeight = if (index == 1) FontWeight.Bold else FontWeight.Medium,
                                        fontSize = 13.sp,
                                        color = if (index == 1) PrimaryMaroon else TextGray
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
                onRefresh = { viewModel.refresh() },
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color(0xFFFAFAFA)),
                    contentPadding = PaddingValues(20.dp)
                ) {
                item {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onNavigateBack() },
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                            tint = PrimaryMaroon
                        )
                        Text("Return to Lab Workstation", fontSize = 13.sp, color = PrimaryMaroon, fontWeight = FontWeight.Bold)
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = uiState.sampleName,
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Black,
                        color = Color.Black,
                        lineHeight = 34.sp
                    )
                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)) {
                        Surface(color = PrimaryMaroon.copy(0.1f), shape = RoundedCornerShape(6.dp)) {
                            Text(
                                text = "ID: ${uiState.sampleId}",
                                color = PrimaryMaroon,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Black,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Analyzed ${uiState.analysisDate} • ${uiState.magnification}",
                            fontSize = 12.sp,
                            color = TextGray
                        )
                    }
                }

                item {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        OutlinedButton(
                            onClick = onCompareSample,
                            modifier = Modifier.weight(1f).height(48.dp),
                            shape = RoundedCornerShape(12.dp),
                            border = BorderStroke(1.dp, Color(0xFFEEEEEE)),
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = Color.Black),
                            contentPadding = PaddingValues(horizontal = 8.dp)
                        ) {
                            Icon(Icons.AutoMirrored.Outlined.CompareArrows, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Compare", fontSize = 13.sp, fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Button(
                            onClick = { },
                            modifier = Modifier.weight(1.2f).height(48.dp),
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryMaroon),
                            contentPadding = PaddingValues(horizontal = 8.dp)
                        ) {
                            Icon(Icons.Outlined.FileDownload, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Export Report", fontSize = 13.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                }

                if (uiState.errorMessage != null) {
                    item {
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(12.dp),
                            color = Color(0xFFFFEBEE),
                            border = BorderStroke(1.dp, Color(0xFFFFCDD2))
                        ) {
                            Row(
                                modifier = Modifier.padding(16.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text("Failed to load analysis record", fontWeight = FontWeight.Bold, color = Color(0xFFC62828), fontSize = 14.sp)
                                    Text(uiState.errorMessage ?: "", fontSize = 12.sp, color = Color(0xFFD32F2F))
                                }
                                Button(
                                    onClick = { viewModel.refresh() },
                                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryMaroon),
                                    shape = RoundedCornerShape(8.dp),
                                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                                ) {
                                    Text("Retry", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }

                if (uiState.isLoading && uiState.sampleId.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(300.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                CircularProgressIndicator(color = PrimaryMaroon, strokeWidth = 3.dp)
                                Spacer(modifier = Modifier.height(16.dp))
                                Text("Loading scientific analysis metrics...", fontSize = 13.sp, color = TextGray)
                            }
                        }
                    }
                } else {
                    item {
                        ResultsMetricGrid(uiState)
                        Spacer(modifier = Modifier.height(24.dp))
                    }

                    item {
                        VisualizationSection(uiState.currentDisplayImageUrl, uiState.inspectionMode, viewModel::setInspectionMode)
                        Spacer(modifier = Modifier.height(24.dp))
                    }
                }

                item {
                    NoduleSizeSpatialMetricsSection(uiState)
                    Spacer(modifier = Modifier.height(24.dp))
                }

                item {
                    AlizarinBreakdown(uiState.spectralBreakdown)
                    Spacer(modifier = Modifier.height(24.dp))
                }

                item {
                    ScientificNotes(uiState.scientificNotes)
                    Spacer(modifier = Modifier.height(40.dp))
                }
            }
        }
    }
    }
}

@Composable
fun NoduleSizeSpatialMetricsSection(state: ResultsState) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.BarChart, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(12.dp))
                Text("Nodule Size & Spatial Metrics", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    NoduleSizeCard("MIN NODULE SIZE", state.minNoduleSize, Modifier.weight(1f))
                    NoduleSizeCard("MAX NODULE SIZE", state.maxNoduleSize, Modifier.weight(1f))
                }
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    NoduleSizeCard("MEAN NODULE SIZE", state.meanNoduleSize, Modifier.weight(1f), isHighlighted = true)
                    NoduleSizeCard("MEDIAN NODULE SIZE", state.medianNoduleSize, Modifier.weight(1f))
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            Text("NODULE SIZE DISTRIBUTION:", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = TextGray)
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                DistributionCard(state.dotCount, "Dot", Modifier.weight(1f))
                DistributionCard(state.smallCount, "Small", Modifier.weight(1f))
                DistributionCard(state.mediumCount, "Medium", Modifier.weight(1f))
                DistributionCard(state.largeCount, "Large", Modifier.weight(1f))
                DistributionCard(state.plaqueCount, "Plaque", Modifier.weight(1f))
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = Color(0xFFFDFDFD),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, Color(0xFFF5F5F5))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Spatial Mineralization Pattern:", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = PrimaryMaroon)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(state.spatialPattern, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Black)
                }
            }
        }
    }
}

@Composable
fun NoduleSizeCard(label: String, value: String, modifier: Modifier, isHighlighted: Boolean = false) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        color = Color(0xFFF8F9FA),
        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(label, fontSize = 9.sp, fontWeight = FontWeight.Bold, color = TextGray)
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                fontSize = 16.sp,
                fontWeight = FontWeight.Black,
                color = if (isHighlighted) PrimaryMaroon else Color.Black
            )
        }
    }
}

@Composable
fun DistributionCard(count: String, label: String, modifier: Modifier) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(10.dp),
        color = Color(0xFFF8F9FA),
        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
    ) {
        Column(
            modifier = Modifier.padding(vertical = 10.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(count, fontSize = 14.sp, fontWeight = FontWeight.Black, color = PrimaryMaroon)
            Text(label, fontSize = 9.sp, fontWeight = FontWeight.Bold, color = TextGray)
        }
    }
}

@Composable
fun ResultsMetricGrid(state: ResultsState) {
    Column {
        Row(modifier = Modifier.fillMaxWidth()) {
            MetricCard(
                label = "MINERALIZED AREA",
                value = state.mineralizedAreaFraction,
                subLabel = state.areaDensityLabel,
                modifier = Modifier.weight(1f),
                indicatorColor = SuccessGreen,
                icon = Icons.Default.FilterCenterFocus
            )
            Spacer(modifier = Modifier.width(16.dp))
            MetricCard(
                label = "STAIN INTENSITY",
                value = state.stainIntensity,
                subLabel = state.absorbanceLabel,
                modifier = Modifier.weight(1f),
                indicatorColor = Color(0xFFD32F2F),
                icon = Icons.Default.BlurOn
            )
        }
        Spacer(modifier = Modifier.height(12.dp))
        Row(modifier = Modifier.fillMaxWidth()) {
            MetricCard(
                label = "NODULE COUNT",
                value = state.calcifiedNodules,
                subLabel = state.noduleLabel,
                modifier = Modifier.weight(1f),
                indicatorColor = Color(0xFFF57C00),
                icon = Icons.Default.Grain
            )
            Spacer(modifier = Modifier.width(16.dp))
            MetricCard(
                label = "EST. CALCIUM",
                value = state.estimatedCalcium,
                subLabel = state.calciumLabel,
                modifier = Modifier.weight(1f),
                indicatorColor = Color(0xFF0288D1),
                icon = Icons.Default.Biotech
            )
        }
        Spacer(modifier = Modifier.height(16.dp))
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            color = Color.White,
            border = BorderStroke(1.dp, Color(0xFFEEEEEE))
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    color = Color(0xFFE8EAF6),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.size(40.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(Icons.Default.Psychology, contentDescription = null, tint = Color(0xFF3F51B5), modifier = Modifier.size(24.dp))
                    }
                }
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text("AI CONFIDENCE & PERFORMANCE", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = TextGray)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(state.aiConfidence, fontSize = 18.sp, fontWeight = FontWeight.Black)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("Processed in ${state.runtime}", fontSize = 12.sp, color = SuccessGreen, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun MetricCard(label: String, value: String, subLabel: String, modifier: Modifier, indicatorColor: Color, icon: ImageVector) {
    Surface(
        modifier = modifier.shadow(2.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(label, fontSize = 10.sp, fontWeight = FontWeight.Bold, color = TextGray)
                Icon(icon, contentDescription = null, tint = indicatorColor.copy(0.6f), modifier = Modifier.size(16.dp))
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(value, fontSize = 22.sp, fontWeight = FontWeight.Black, color = Color.Black)
            Text(subLabel, fontSize = 11.sp, color = SuccessGreen, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun VisualizationSection(overlayUrl: String?, currentMode: InspectionMode, onModeChange: (InspectionMode) -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Layers, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(20.dp))
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Interactive Visualization", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Surface(
                color = Color(0xFFF5F5F5),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(modifier = Modifier.padding(4.dp), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    InspectionModeTab("MICROGRAPH", currentMode == InspectionMode.Original, Modifier.weight(1f)) { onModeChange(InspectionMode.Original) }
                    InspectionModeTab("SEGMENTATION", currentMode == InspectionMode.Segmentation, Modifier.weight(1f)) { onModeChange(InspectionMode.Segmentation) }
                    InspectionModeTab("HEATMAP", currentMode == InspectionMode.Heatmap, Modifier.weight(1f)) { onModeChange(InspectionMode.Heatmap) }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(260.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color.Black),
                contentAlignment = Alignment.Center
            ) {
                if (!overlayUrl.isNullOrEmpty()) {
                    AsyncImage(
                        model = overlayUrl,
                        contentDescription = "Analysis Overlay Micrograph",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    )
                } else {
                    Box(modifier = Modifier.fillMaxSize().background(
                        Brush.radialGradient(
                            colors = listOf(Color(0xFF3D0808), Color.Black),
                            radius = 800f
                        )
                    ))
                    
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.Visibility, contentDescription = null, tint = Color.White.copy(alpha = 0.2f), modifier = Modifier.size(56.dp))
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("${currentMode.name} VIEW ACTIVE", color = Color.White.copy(alpha = 0.5f), fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    }
                }
                
                Box(
                    modifier = Modifier.align(Alignment.BottomStart).padding(16.dp)
                ) {
                    Surface(color = Color.Black.copy(alpha = 0.7f), shape = RoundedCornerShape(6.dp)) {
                        Row(modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                            Box(modifier = Modifier.size(8.dp).background(PrimaryMaroon, CircleShape))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "AI Segmentation Active",
                                color = Color.White,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
                
                IconButton(
                    onClick = { },
                    modifier = Modifier.align(Alignment.TopEnd).padding(8.dp)
                ) {
                    Icon(Icons.Default.Fullscreen, contentDescription = "Full Screen", tint = Color.White)
                }
            }
        }
    }
}

@Composable
fun InspectionModeTab(label: String, isSelected: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Surface(
        modifier = modifier.clickable { onClick() },
        color = if (isSelected) Color.White else Color.Transparent,
        shape = RoundedCornerShape(10.dp),
        shadowElevation = if (isSelected) 2.dp else 0.dp
    ) {
        Text(
            text = label,
            fontSize = 10.sp,
            fontWeight = FontWeight.Black,
            color = if (isSelected) PrimaryMaroon else TextGray,
            modifier = Modifier.padding(vertical = 10.dp),
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun AlizarinBreakdown(items: List<SpectralItem>) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.BarChart, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(12.dp))
                Text("Spectral Absorbance Breakdown", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(20.dp))
            items.forEachIndexed { index, item ->
                SpectralListItem(item)
                if (index < items.size - 1) {
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
    }
}

@Composable
fun SpectralListItem(item: SpectralItem) {
    Column {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.Bottom) {
            Text(item.name, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = Color.Black)
            Text("${item.percentage}%", fontSize = 14.sp, fontWeight = FontWeight.Black, color = PrimaryMaroon)
        }
        Spacer(modifier = Modifier.height(8.dp))
        LinearProgressIndicator(
            progress = { item.percentage.toFloat() / 100f },
            modifier = Modifier.fillMaxWidth().height(8.dp).clip(CircleShape),
            color = item.color,
            trackColor = Color(0xFFF5F5F5)
        )
    }
}

@Composable
fun ScientificNotes(notes: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        color = Color(0xFFFFF8F8),
        border = BorderStroke(1.dp, PrimaryMaroon.copy(alpha = 0.1f))
    ) {
        Row(modifier = Modifier.padding(16.dp)) {
            Icon(Icons.Default.Info, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(20.dp))
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text("Scientific Interpretation:", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = PrimaryMaroon)
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = notes, 
                    fontSize = 12.sp, 
                    color = Color.Black.copy(alpha = 0.7f), 
                    lineHeight = 18.sp,
                    textAlign = TextAlign.Start
                )
            }
        }
    }
}
