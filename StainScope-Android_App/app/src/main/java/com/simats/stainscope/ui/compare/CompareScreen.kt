package com.simats.stainscope.ui.compare

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.CompareArrows
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.simats.stainscope.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompareScreen(
    onNavigateToDashboard: () -> Unit,
    onNavigateToAnalysis: () -> Unit,
    onNavigateToReports: () -> Unit,
    onNavigateToProfile: () -> Unit,
    onNavigateBack: () -> Unit,
    viewModel: CompareViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var visible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        visible = true
        viewModel.loadData()
    }

    Scaffold(
        topBar = {
            Column(modifier = Modifier.background(MaterialTheme.colorScheme.surface)) {
                TopAppBar(
                    title = {
                        Text(
                            text = "Comparison Tool", 
                            fontWeight = FontWeight.Black, 
                            fontSize = 22.sp
                        ) 
                    },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack, 
                                contentDescription = "Back"
                            )
                        }
                    },
                    actions = {
                        IconButton(onClick = { }) {
                            Icon(Icons.Outlined.Notifications, contentDescription = "Notifications")
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
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                        titleContentColor = MaterialTheme.colorScheme.onSurface,
                        navigationIconContentColor = MaterialTheme.colorScheme.onSurface,
                        actionIconContentColor = MaterialTheme.colorScheme.onSurface
                    )
                )
                
                ScrollableTabRow(
                    selectedTabIndex = 2,
                    containerColor = MaterialTheme.colorScheme.surface,
                    contentColor = PrimaryMaroon,
                    edgePadding = 16.dp,
                    divider = {},
                    indicator = { tabPositions ->
                        if (tabPositions.size > 2) {
                            TabRowDefaults.SecondaryIndicator(
                                Modifier.tabIndicatorOffset(tabPositions[2]),
                                color = PrimaryMaroon,
                                height = 3.dp
                            )
                        }
                    }
                ) {
                    val tabs = listOf(
                        "Dashboard" to Icons.Outlined.Dashboard,
                        "Upload & Analyze" to Icons.Outlined.CloudUpload,
                        "Compare" to Icons.AutoMirrored.Filled.CompareArrows,
                        "Reports" to Icons.Outlined.Description
                    )
                    tabs.forEachIndexed { index, pair ->
                        val isSelected = index == 2
                        Tab(
                            selected = isSelected,
                            onClick = { 
                                when(index) {
                                    0 -> onNavigateToDashboard()
                                    1 -> onNavigateToAnalysis()
                                    2 -> { /* Already here */ }
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
                                        tint = if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = pair.first, 
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        fontSize = 13.sp,
                                        color = if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        )
                    }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
            }
        }
    ) { padding ->
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600)) + slideInVertically(initialOffsetY = { 60 })
        ) {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .background(MaterialTheme.colorScheme.background),
                contentPadding = PaddingValues(20.dp),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                // 1. Header Section
                item {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Default.Science,
                                contentDescription = null,
                                tint = PrimaryMaroon,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                "Multi-Sample Alizarin Red Differential",
                                color = PrimaryMaroon,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Black,
                                letterSpacing = 0.5.sp
                            )
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Biomedical Comparison Map",
                            fontSize = 28.sp,
                            fontWeight = FontWeight.Black,
                            color = MaterialTheme.colorScheme.onBackground,
                            lineHeight = 34.sp
                        )
                        Text(
                            text = "Interactive split viewer and quantitative differential matrix for selected reports.",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(top = 8.dp, bottom = 16.dp)
                        )
                        
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            ActionChipButton(
                                Icons.Outlined.FileDownload,
                                "Export PDF",
                                PrimaryMaroon,
                                Color.White,
                                Modifier.weight(1f)
                            )
                            ActionChipButton(
                                Icons.Outlined.TableChart,
                                "CSV",
                                MaterialTheme.colorScheme.surface,
                                MaterialTheme.colorScheme.onSurface,
                                Modifier.weight(0.7f)
                            )
                        }
                    }
                }

                // 2. Sample Selection Section
                item {
                    SelectionSection(uiState, viewModel)
                }

                if (uiState.isComparing) {
                    // 3. Sample A/B cards
                    item {
                        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                            uiState.selectedSamples.forEachIndexed { index, sample ->
                                if (index > 0) {
                                    Box(
                                        modifier = Modifier.fillMaxWidth(),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Surface(
                                            shape = CircleShape,
                                            color = MaterialTheme.colorScheme.surface,
                                            shadowElevation = 2.dp,
                                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                                            modifier = Modifier.size(32.dp)
                                        ) {
                                            Icon(
                                                Icons.Default.SwapVert,
                                                contentDescription = null,
                                                tint = PrimaryMaroon,
                                                modifier = Modifier.padding(6.dp)
                                            )
                                        }
                                    }
                                }
                                DetailedCompareCard(
                                    label = if (index == 0) "SAMPLE A (BASELINE)" else "SAMPLE B (EXPERIMENTAL)",
                                    sample = sample,
                                    color = if (index == 0) Color(0xFFF57C00) else PrimaryMaroon
                                )
                            }
                        }
                    }

                    // 4 & 5. Comparison viewer & Viewer controls
                    item {
                        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                            SplitViewerSection(uiState, viewModel)
                            
                            // Viewer controls grouped together directly below comparison viewer
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                ViewerActionButton(
                                    Icons.Default.ZoomIn, 
                                    "Zoom: ${(uiState.zoom * 100).toInt()}%", 
                                    Modifier.weight(1f)
                                )
                                ViewerActionButton(
                                    Icons.Default.CenterFocusStrong, 
                                    "AI Align", 
                                    Modifier.weight(1f)
                                )
                                ViewerActionButton(
                                    Icons.Default.Refresh, 
                                    "Reset", 
                                    Modifier.weight(1f)
                                )
                            }
                        }
                    }

                    // 6. Quantitative Matrix
                    item {
                        ComparisonMetricsTable(uiState)
                    }

                    // 7. AI Differential Conclusion
                    item {
                        ScientificDifferentialConclusion()
                    }
                    
                    item {
                        Spacer(modifier = Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

@Composable
fun ActionChipButton(
    icon: ImageVector,
    label: String,
    bgColor: Color,
    contentColor: Color,
    modifier: Modifier
) {
    Surface(
        modifier = modifier.height(38.dp),
        shape = RoundedCornerShape(8.dp),
        color = bgColor,
        border = if (bgColor != PrimaryMaroon) BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant) else null
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Icon(icon, contentDescription = null, modifier = Modifier.size(16.dp), tint = contentColor)
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                label,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = contentColor,
                maxLines = 1
            )
        }
    }
}

@Composable
fun SelectionSection(state: CompareState, viewModel: CompareViewModel) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.FilterList,
                        contentDescription = null,
                        tint = PrimaryMaroon,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        "Reports Selection",
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                }
                Surface(
                    color = PrimaryMaroon.copy(alpha = 0.1f),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        "${state.selectedReportIds.size} Selected",
                        color = PrimaryMaroon,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // LazyRow for reports with content padding to prevent clipping
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(horizontal = 4.dp)
            ) {
                items(state.availableReports) { report ->
                    ReportSelectionCard(
                        report = report,
                        isSelected = state.selectedReportIds.contains(report.id),
                        onToggle = { viewModel.toggleReportSelection(report.id) }
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { viewModel.startComparison() },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(10.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryMaroon),
                contentPadding = PaddingValues(vertical = 12.dp)
            ) {
                Icon(
                    Icons.AutoMirrored.Filled.CompareArrows,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "Apply Comparison",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun ReportSelectionCard(report: ReportSummary, isSelected: Boolean, onToggle: () -> Unit) {
    Surface(
        modifier = Modifier.width(220.dp).clickable { onToggle() },
        shape = RoundedCornerShape(12.dp),
        color = if (isSelected) PrimaryMaroon.copy(alpha = 0.05f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
        border = BorderStroke(1.dp, if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Checkbox(
                    checked = isSelected,
                    onCheckedChange = { onToggle() },
                    colors = CheckboxDefaults.colors(checkedColor = PrimaryMaroon),
                    modifier = Modifier.size(24.dp)
                )
                Surface(color = report.dayColor.copy(alpha = 0.2f), shape = RoundedCornerShape(4.dp)) {
                    Text(
                        report.day,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(report.id, fontSize = 10.sp, color = PrimaryMaroon, fontWeight = FontWeight.Black)
            Text(
                report.name,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Area: ${report.area}", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text("OD: ${report.od}", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

@Composable
fun DetailedCompareCard(label: String, sample: CompareSample, color: Color) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    label,
                    color = color,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp
                )
                Text(sample.id, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 10.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                sample.name, 
                fontSize = 15.sp, 
                fontWeight = FontWeight.Bold, 
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(16.dp))
            Row(
                modifier = Modifier.fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f), RoundedCornerShape(8.dp))
                    .padding(12.dp)
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text("TREATMENT", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(
                        sample.treatment,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
                Column(modifier = Modifier.weight(1f)) {
                    Text("TIMELINE", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(
                        sample.timeline,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
            Row(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.weight(1f)) {
                    Text("Mineralized Area %", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(
                        sample.mineralizedArea,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Black,
                        color = color
                    )
                }
                Column(modifier = Modifier.weight(1f)) {
                    Text("Stain Intensity OD", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(
                        sample.stainIntensity,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Black,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                }
            }
        }
    }
}

@Composable
fun SplitViewerSection(state: CompareState, viewModel: CompareViewModel) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Layers,
                        contentDescription = null,
                        tint = PrimaryMaroon,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        "Split Micrograph Viewer",
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Mode Toggles
            Surface(
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(4.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    ViewModeTab(
                        "ORIGINAL",
                        state.inspectionMode == CompareInspectionMode.Original,
                        Modifier.weight(1f)
                    ) { viewModel.setInspectionMode(CompareInspectionMode.Original) }
                    ViewModeTab(
                        "SEGMENTED",
                        state.inspectionMode == CompareInspectionMode.Segmentation,
                        Modifier.weight(1f)
                    ) { viewModel.setInspectionMode(CompareInspectionMode.Segmentation) }
                    ViewModeTab(
                        "HEATMAP",
                        state.inspectionMode == CompareInspectionMode.Heatmap,
                        Modifier.weight(1f)
                    ) { viewModel.setInspectionMode(CompareInspectionMode.Heatmap) }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Box(
                modifier = Modifier.fillMaxWidth().height(260.dp).clip(RoundedCornerShape(16.dp))
                    .background(Color.Black),
                contentAlignment = Alignment.Center
            ) {
                Box(
                    modifier = Modifier.fillMaxSize().background(
                        Brush.radialGradient(
                            colors = listOf(Color(0xFF3D0808), Color.Black),
                            radius = 800f
                        )
                    )
                )

                // Split Line
                Box(modifier = Modifier.fillMaxHeight().width(2.dp).background(Color.White.copy(0.3f)))

                // Labels
                Box(modifier = Modifier.fillMaxSize().padding(12.dp)) {
                    Surface(
                        color = Color.Black.copy(0.6f),
                        shape = RoundedCornerShape(4.dp),
                        modifier = Modifier.align(Alignment.BottomStart)
                    ) {
                        Text(
                            "CONTROL",
                            color = Color.White,
                            fontSize = 8.sp,
                            fontWeight = FontWeight.Black,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                        )
                    }
                    Surface(
                        color = PrimaryMaroon.copy(0.8f),
                        shape = RoundedCornerShape(4.dp),
                        modifier = Modifier.align(Alignment.BottomEnd)
                    ) {
                        Text(
                            "TEST",
                            color = Color.White,
                            fontSize = 8.sp,
                            fontWeight = FontWeight.Black,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                        )
                    }
                }

                Surface(
                    modifier = Modifier.size(36.dp).shadow(4.dp, CircleShape),
                    shape = CircleShape,
                    color = Color.White,
                    border = BorderStroke(2.dp, PrimaryMaroon)
                ) {
                    Icon(
                        Icons.Default.Compare,
                        contentDescription = null,
                        tint = PrimaryMaroon,
                        modifier = Modifier.padding(8.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun ViewModeTab(label: String, isSelected: Boolean, modifier: Modifier, onClick: () -> Unit) {
    Surface(
        modifier = modifier.clickable { onClick() },
        color = if (isSelected) MaterialTheme.colorScheme.surface else Color.Transparent,
        shape = RoundedCornerShape(8.dp),
        shadowElevation = if (isSelected) 2.dp else 0.dp
    ) {
        Text(
            text = label,
            fontSize = 9.sp,
            fontWeight = FontWeight.Black,
            color = if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(vertical = 10.dp),
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun ViewerActionButton(icon: ImageVector, label: String, modifier: Modifier) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(8.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Row(
            modifier = Modifier.padding(vertical = 10.dp, horizontal = 4.dp),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(icon, contentDescription = null, modifier = Modifier.size(14.dp), tint = PrimaryMaroon)
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = label, 
                fontSize = 10.sp, 
                fontWeight = FontWeight.Bold, 
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1
            )
        }
    }
}

@Composable
fun ComparisonMetricsTable(state: CompareState) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.Analytics,
                    contentDescription = null,
                    tint = PrimaryMaroon,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text("Quantitative Comparison Matrix", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(20.dp))

            CompareMetricRow("METRIC", "CONTROL", "TEST", isHeader = true)
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant, modifier = Modifier.padding(vertical = 4.dp))
            CompareMetricRow(
                "Mineralized Area",
                state.selectedSamples[0].mineralizedArea,
                state.selectedSamples[1].mineralizedArea
            )
            CompareMetricRow(
                "Stain Intensity",
                state.selectedSamples[0].stainIntensity,
                state.selectedSamples[1].stainIntensity
            )
            CompareMetricRow(
                "Nodule Count",
                state.selectedSamples[0].noduleCount,
                state.selectedSamples[1].noduleCount
            )
            CompareMetricRow(
                "Avg Nodule Size",
                state.selectedSamples[0].avgNoduleSize,
                state.selectedSamples[1].avgNoduleSize
            )
            CompareMetricRow(
                "Calcium Density",
                state.selectedSamples[0].calciumDensity,
                state.selectedSamples[1].calciumDensity
            )
            CompareMetricRow(
                "AI Confidence",
                state.selectedSamples[0].aiConfidence,
                state.selectedSamples[1].aiConfidence
            )
        }
    }
}

@Composable
fun CompareMetricRow(label: String, valA: String, valB: String, isHeader: Boolean = false) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            label,
            modifier = Modifier.weight(1.2f),
            fontSize = 11.sp,
            fontWeight = if (isHeader) FontWeight.Black else FontWeight.Bold,
            color = if (isHeader) MaterialTheme.colorScheme.onSurfaceVariant else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f)
        )
        Text(
            valA,
            modifier = Modifier.weight(1f),
            fontSize = 12.sp,
            fontWeight = if (isHeader) FontWeight.Black else FontWeight.Bold,
            color = if (isHeader) MaterialTheme.colorScheme.onSurfaceVariant else MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.Center
        )
        Text(
            valB,
            modifier = Modifier.weight(1f),
            fontSize = 13.sp,
            fontWeight = if (isHeader) FontWeight.Black else FontWeight.Black,
            color = if (isHeader) MaterialTheme.colorScheme.onSurfaceVariant else PrimaryMaroon,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun ScientificDifferentialConclusion() {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = SuccessGreen.copy(alpha = 0.08f),
        border = BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.2f))
    ) {
        Row(modifier = Modifier.padding(20.dp)) {
            Icon(
                Icons.Default.Psychology,
                contentDescription = null,
                tint = SuccessGreen,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(
                    "AI DIFFERENTIAL INTERPRETATION",
                    fontWeight = FontWeight.Black,
                    fontSize = 12.sp,
                    color = SuccessGreen,
                    letterSpacing = 1.sp
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Significant osteogenic progression detected in Sample B. Quantitative data shows a 25.6% increase in mineralized matrix density compared to Baseline Sample A. Patterns are consistent with induced BMP-2 differentiation.",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurface,
                    lineHeight = 20.sp
                )
            }
        }
    }
}
